"""
Spike detection (v2: zero-filled windows + Poisson test).

complaint_windows holds one row per (case, 6-hour window) that received at
least one complaint, so empty windows are missing. v2 puts them back as 0,
builds a smoothed 7-day baseline rate, and flags the current window when it
has at least MIN_COUNT complaints and that count is very unlikely under the
baseline (Poisson tail probability < P_SPIKE). A brand-new case is judged
against the prior rate, so a new problem can alert.

Chosen and tested offline (experiments/dedup/spike_sim.py,
results/spike_detector_v2_rule.md): on a fresh Firefox sample it caught 75% of
simulated outbreaks with 1.7 false alerts per 100 windows; the old z-score
detector caught 0%.
"""

import math
from datetime import datetime, timedelta

import numpy as np

from backend.database.supabase import (
    get_case_history,
    get_case_history_bulk,
)

WINDOW_HOURS = 6
BASELINE_WINDOWS = 28          # 7 days of 6-hour windows
PRIOR_COUNT = 0.5              # prior: about one complaint every two weeks
PRIOR_WINDOWS = 7
MIN_COUNT = 2
GROUP_MIN_COUNT = 3            # alert groups (several related cases) need one more complaint
P_SPIKE = 0.001
P_CRITICAL = 0.00001


def compute_z_score(
    history,
    current
):
    """Old z-score (kept for scripts that report it)."""

    if len(history) < 7:
        return 0

    mean = np.mean(history)

    std = np.std(history)

    if std == 0:
        return 0

    return (
        current - mean
    ) / std


def poisson_tail(count, rate):
    """P(X >= count) for X ~ Poisson(rate)."""

    if count <= 0:
        return 1.0

    term = math.exp(-rate)
    below = term
    for k in range(1, count):
        term *= rate / k
        below += term

    return max(0.0, 1.0 - below)


def _parse(ts):

    if isinstance(ts, datetime):
        return ts

    return datetime.fromisoformat(
        str(ts).replace("Z", "+00:00")
    )


def window_counts(history):
    """
    Rows ({window_start, complaint_ct}) -> zero-filled counts, oldest first,
    ending at the case's latest window.
    """

    if not history:
        return []

    by_start = {}
    for row in history:
        start = _parse(row["window_start"])
        by_start[start] = by_start.get(start, 0) + int(row["complaint_ct"] or 0)

    first, last = min(by_start), max(by_start)
    step = timedelta(hours=WINDOW_HOURS)
    n = int(round((last - first) / step)) + 1

    return [
        by_start.get(first + i * step, 0)
        for i in range(n)
    ]


def evaluate_counts(counts, min_count=MIN_COUNT):
    """Detector v2 on zero-filled counts; the last entry is the current window."""

    current = int(counts[-1]) if counts else 0
    previous = counts[:-1][-BASELINE_WINDOWS:]

    rate = (
        (sum(previous) + PRIOR_COUNT)
        / (len(previous) + PRIOR_WINDOWS)
    )

    p_value = poisson_tail(current, rate)

    spike = current >= min_count and p_value < P_SPIKE

    return {

        "spike": bool(spike),

        "critical": bool(spike and p_value < P_CRITICAL),

        # Poisson z, for display only
        "z_score": float(round((current - rate) / math.sqrt(rate), 2)),

        "current": current,

        "baseline_rate": float(round(rate, 3)),

        "p_value": float(p_value),

        "detector": "poisson_v2",
    }


def detect_from_history(history):

    result = evaluate_counts(
        window_counts(history)
    )

    if history:
        result["window_start"] = str(
            max(_parse(r["window_start"]) for r in history)
        )

    return result


def detect_group_from_history(history):
    """Spike check for an alert group: complaint_windows rows of all its cases,
    summed per window (window_counts adds rows with the same window_start)."""

    result = evaluate_counts(
        window_counts(history),
        min_count=GROUP_MIN_COUNT,
    )

    if history:
        result["window_start"] = str(
            max(_parse(r["window_start"]) for r in history)
        )

    return result


def detect_spike(case_id):

    return detect_from_history(
        get_case_history(case_id)
    )


def detect_spikes_bulk(cases, history_by_case):

    return {
        case["case_id"]: detect_from_history(
            history_by_case.get(case["case_id"], [])
        )
        for case in cases
    }
