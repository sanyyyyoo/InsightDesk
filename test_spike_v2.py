"""
Offline checks for spike detector v2 (no Supabase, no network).

  python test_spike_v2.py
"""

import os
import sys
import types
from datetime import datetime, timedelta, timezone

import numpy as np

# the detector imports the Supabase client module; stub it so nothing connects
stub = types.ModuleType("backend.database.supabase")
stub.get_case_history = lambda case_id: []
stub.get_case_history_bulk = lambda case_ids: []
sys.modules["backend.database.supabase"] = stub

from backend.services.spike_detection import (  # noqa: E402
    detect_from_history,
    detect_spikes_bulk,
    window_counts,
)

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)


def rows(counts):
    """Zero-filled counts -> complaint_windows rows (empty windows not stored, like the app)."""
    return [
        {"window_start": (T0 + timedelta(hours=6 * i)).isoformat(), "complaint_ct": c}
        for i, c in enumerate(counts) if c > 0
    ]


def check(name, counts, expect):
    r = detect_from_history(rows(counts))
    ok = r["spike"] == expect
    print(f"{'ok  ' if ok else 'FAIL'} {name}: spike={r['spike']} current={r['current']} "
          f"rate={r['baseline_rate']} p={r['p_value']:.2e}")
    return ok


def scenarios():
    return all([
        check("no history", [], False),
        check("brand-new case, 1 complaint", [1], False),
        check("brand-new case, 3 complaints in one window", [3], True),
        check("steady 1 per window for a week, then 1", [1] * 28 + [1], False),
        check("steady 1 per window, then 3", [1] * 28 + [3], False),
        check("quiet week (one complaint), then 4", [1] + [0] * 27 + [4], True),
        check("quiet week, then single complaint", [1] + [0] * 27 + [1], False),
        check("busy case: 5 per window, then 12", [5] * 28 + [12], True),
        check("busy case: 5 per window, then 8", [5] * 28 + [8], False),
        window_counts(rows([2, 0, 0, 1])) == [2, 0, 0, 1],
        detect_spikes_bulk([{"case_id": 7}], {})[7]["spike"] is False,
    ])


def matches_experiment(trials=300, seed=1):
    """Same decisions as the offline-tested detector (experiments/dedup/spike_sim.py)."""
    sys.path.insert(0, "D:/PBL/InsightDesk-dedup/experiments/dedup")
    try:
        from spike_sim import make_detector_v2
    except Exception as e:                      # experiments clone not present
        print("skip equivalence check:", e)
        return True
    det = make_detector_v2(2, 0.001)
    rng = np.random.default_rng(seed)
    mismatches = 0
    for _ in range(trials):
        counts = rng.poisson(rng.uniform(0.02, 1.5), size=(1, 60)).astype(float)
        counts[0, rng.integers(10, 60)] += rng.integers(0, 6)
        nz = np.where(counts[0] > 0)[0]
        if not len(nz):
            continue
        first = np.array([nz[0]])
        exp = det(counts, first)[0]
        for t in nz:
            app = detect_from_history(rows(list(counts[0, nz[0]:t + 1].astype(int))))["spike"]
            mismatches += int(app != bool(exp[t]))
    print(f"{'ok  ' if mismatches == 0 else 'FAIL'} matches offline detector: {mismatches} mismatches")
    return mismatches == 0


if __name__ == "__main__":
    os.environ.setdefault("OMP_NUM_THREADS", "4")
    good = scenarios() & matches_experiment()
    print("ALL PASSED" if good else "SOME CHECKS FAILED")
    sys.exit(0 if good else 1)
