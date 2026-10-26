"""
Unassigned-complaint spikes: a separate outage-detection signal (not deduplication).

R1 puts every complaint its judge calls not specific ("app not working!!") in its own case
(cases.is_vague), so those complaints can never build up a case spike. During an outage most
people write exactly such complaints. This counts them per product in the same 6-hour windows
as case spikes and runs the same detector v2 (MIN_COUNT 2, P_SPIKE 0.001, smoothed 7-day
baseline per product), so a burst far above that product's normal level raises one alert:
"possible outage or widespread degradation" - an early warning, not a diagnosis.

Tested offline before adoption (experiments/dedup/results/vague_counter_confirm_rule.md):
on three new help-desk apps, simulated bursts of 10 such complaints were caught in 100% of
trials (cases only: 0%) for +0.19 false alerts per 100 windows. Note: against human labels most
of these complaints are in fact specific but unplaced by the judge (its vague flag agrees with
the people's "unspecified" label 17% of the time), hence "unassigned", not "vague".

Windows are stamped when the app receives a complaint (upsert_complaint_window), so a late review
counts in its arrival window. On by default (UNASSIGNED_SPIKES=0 turns it off).
"""

import os
from collections import defaultdict
from datetime import timedelta

from backend.services.spike_detection import WINDOW_HOURS, _parse, evaluate_counts, window_counts

CHUNK = 200                     # case ids per complaint_windows query (keeps under the 1,000-row page)
CONTEXT_CASES = 5               # specific cases shown next to an alert


def enabled():
    return os.getenv("UNASSIGNED_SPIKES", "1") == "1"


def incident_start(counts, starts):
    """First window of the run of consecutive alerting windows that ends at the current window
    (one incident = one alert; product + incident_start is a stable key for notifications)."""
    first = len(counts) - 1
    while first > 0 and evaluate_counts(counts[:first])["spike"]:
        first -= 1
    return starts[first]


def detect(vague_case_ids_by_product, history_rows, now=None):
    """Pure function. vague_case_ids_by_product: {product: [case_id]}; history_rows: complaint_windows
    rows ({case_id, window_start, complaint_ct}) of those cases. With `now`, empty windows up to the
    current window are counted as 0, so an old burst is not reported as an active alert (case spikes
    are evaluated at the case's latest window instead). Returns one result per product."""
    product_of = {c: p for p, ids in vague_case_ids_by_product.items() for c in ids}
    rows_by_product = defaultdict(list)
    for r in history_rows:
        p = product_of.get(r["case_id"])
        if p is not None:
            rows_by_product[p].append(r)
    out = []
    for product, rows in rows_by_product.items():
        counts = window_counts(rows)
        first = min(_parse(r["window_start"]) for r in rows)
        step = timedelta(hours=WINDOW_HOURS)
        if now is not None:                     # zero-fill to the current window
            current = first + int((_parse(now) - first) // step) * step
            counts = counts + [0] * max(0, int(round((current - first) / step)) + 1 - len(counts))
        result = evaluate_counts(counts)
        starts = [first + i * step for i in range(len(counts))]
        result.update({
            "product": product,
            "window_start": str(starts[-1]),
            "unassigned_cases": len(vague_case_ids_by_product.get(product, [])),
        })
        if result["spike"]:
            result["incident_start"] = str(incident_start(counts, starts))
            result["message"] = (f"{product}: {result['current']} unassigned complaints in the last "
                                 f"{WINDOW_HOURS} h (normal about {result['baseline_rate']:.1f}). "
                                 "Possible outage or widespread degradation.")
        out.append(result)
    return sorted(out, key=lambda r: (not r["spike"], r["p_value"]))


def related_cases(product, window_start, cases, product_of_case, history_rows):
    """Specific (non-vague) cases of the product with complaints in the alert window, most first."""
    ws = _parse(window_start)
    n = defaultdict(int)
    for r in history_rows:
        c = r["case_id"]
        if product_of_case.get(c) == product and _parse(r["window_start"]) == ws:
            n[c] += int(r["complaint_ct"] or 0)
    top = sorted(n, key=lambda c: -n[c])[:CONTEXT_CASES]
    return [{"case_id": c, "complaints_in_window": n[c],
             "representative_text": cases.get(c, {}).get("representative_text"),
             "report_count": cases.get(c, {}).get("report_count")} for c in top]
