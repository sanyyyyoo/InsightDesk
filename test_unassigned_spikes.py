"""
Offline checks for unassigned-complaint spikes (no Supabase, no network).

  python test_unassigned_spikes.py
"""

import os
import random
import sys
import types
from datetime import datetime, timedelta, timezone

# stub the Supabase client module so nothing connects
class _Stub(types.ModuleType):
    def __getattr__(self, name):                # any database function -> returns []
        if name.startswith("_"):
            raise AttributeError(name)
        return lambda *a, **k: []


sys.modules["backend.database.supabase"] = _Stub("backend.database.supabase")
sys.modules["backend.services.email_service"] = _Stub("backend.services.email_service")   # no SMTP setup

from backend.services import unassigned_spikes as us  # noqa: E402

T0 = datetime(2026, 10, 1, tzinfo=timezone.utc)
results = []


def ts(i):
    return (T0 + timedelta(hours=6 * i)).isoformat()


def stream(counts, first_case=1):
    """Per-window counts of unassigned complaints -> one vague case per complaint + its window row."""
    ids, rows, c = [], [], first_case
    for i, n in enumerate(counts):
        for _ in range(n):
            ids.append(c)
            rows.append({"case_id": c, "window_start": ts(i), "complaint_ct": 1})
            c += 1
    return ids, rows


def check(name, cond, detail=""):
    results.append(bool(cond))
    print(f"{'ok  ' if cond else 'FAIL'} {name} {detail}")


def one(counts):
    ids, rows = stream(counts)
    return us.detect({"Zendesk": ids}, rows)[0]


# 1. feature flag: off by default
os.environ.pop("UNASSIGNED_SPIKES", None)
check("off by default", not us.enabled())
os.environ["UNASSIGNED_SPIKES"] = "1"
check("on with UNASSIGNED_SPIKES=1", us.enabled())

# 2. outage: about 1 per 4 windows for a week, then 15 in one window
base = [1 if i % 4 == 0 else 0 for i in range(28)]
r = one(base + [15])
check("burst of 15 over a low baseline alerts", r["spike"], f"(current {r['current']}, rate {r['baseline_rate']})")
check("message says possible outage, not a diagnosis", "Possible outage" in r.get("message", ""))
check("incident starts at the burst window", r.get("incident_start") == str(datetime.fromisoformat(ts(28))))

# 3. normal level: no alert
r = one(base + [1])
check("steady level, 1 in current window: no alert", not r["spike"])
r = one([2] * 28 + [3])
check("busy product, 3 vs normal 2: no alert", not r["spike"])

# 4. minimum count 2
r = one([0] * 28 + [1])
check("a single unassigned complaint never alerts", not r["spike"])

# 5. a two-window incident is ONE incident (stable key)
r = one(base + [12, 14])
check("two alerting windows in a row: incident_start = first of them",
      r["spike"] and r.get("incident_start") == str(datetime.fromisoformat(ts(28))), f"({r.get('incident_start')})")

# 5b. an old burst is not an active alert once quiet windows follow (now = 3 days later)
ids, rows = stream(base + [15])
r = us.detect({"Zendesk": ids}, rows, now=ts(28 + 12))[0]
check("burst 3 days ago, quiet since: no active alert", not r["spike"], f"(current {r['current']})")

# 6. products are counted separately
ids_a, rows_a = stream(base + [15])
ids_b, rows_b = stream(base + [1], first_case=10_000)
out = {x["product"]: x for x in us.detect({"Zendesk": ids_a, "Freshdesk": ids_b}, rows_a + rows_b)}
check("burst in one product does not alert the other", out["Zendesk"]["spike"] and not out["Freshdesk"]["spike"])

# 7. same decisions as the offline-tested detector (experiments/dedup/spike_sim.py, m 2, p 0.001)
try:
    sys.path.insert(0, "D:/PBL/InsightDesk-dedup/experiments/dedup")
    import numpy as np
    from spike_sim import make_detector_v2
    det = make_detector_v2(2, 0.001)
    rnd = random.Random(7)
    mism = 0
    for _ in range(300):
        n = rnd.randint(2, 60)
        lam = rnd.choice([0.1, 0.3, 1.0, 3.0])
        counts = [min(40, int(rnd.expovariate(1 / lam))) for _ in range(n)]
        counts[0] = max(1, counts[0])              # series starts at the first stored window
        if rnd.random() < 0.4:
            counts[-1] += rnd.randint(3, 15)
        ids_, rows_ = stream(counts)
        app = us.detect({"P": ids_}, rows_, now=ts(len(counts) - 1))[0]["spike"]
        exp = bool(det(np.array([counts], dtype=float), np.array([0]))[0, -1])
        mism += app != exp
    check("matches the experiment detector on 300 random series", mism == 0, f"({mism} mismatches)")
except ImportError as e:
    print(f"skip  experiment equivalence ({e})")

# 8. related specific cases shown with an alert
cases = {501: {"representative_text": "Google login returns 403", "report_count": 4},
         502: {"representative_text": "notifications late", "report_count": 2}}
hist = [{"case_id": 501, "window_start": ts(28), "complaint_ct": 3},
        {"case_id": 502, "window_start": ts(27), "complaint_ct": 2}]
rel = us.related_cases("Zendesk", ts(28), cases, {501: "Zendesk", 502: "Zendesk"}, hist)
check("related cases = specific cases active in the alert window", [x["case_id"] for x in rel] == [501])

# 9. endpoint with fake data (flag on / off)
from backend.routers import dashboard  # noqa: E402
ids, rows = stream(base + [15])
dashboard.get_cases = lambda: [{"case_id": c, "is_vague": True} for c in ids] + [{"case_id": 501, "is_vague": False,
                                                                                    "representative_text": "x"}]
dashboard.get_complaints = lambda: [{"case_id": c, "product": "Zendesk"} for c in ids + [501]]
dashboard.get_case_history_bulk = lambda case_ids: [r for r in rows + hist if r["case_id"] in set(case_ids)]
class _Clock(datetime):                         # endpoint "now" = the burst window
    @classmethod
    def now(cls, tz=None):
        return datetime.fromisoformat(ts(28))


dashboard.datetime = _Clock
res = dashboard.dashboard_unassigned_spikes()
check("endpoint: alert with related case", res["enabled"] and res["products"][0]["spike"]
      and res["products"][0]["related_cases"][0]["case_id"] == 501)
os.environ["UNASSIGNED_SPIKES"] = "0"
check("endpoint: disabled returns nothing", dashboard.dashboard_unassigned_spikes() == {"enabled": False, "products": []})

print("\nALL PASSED" if all(results) else f"\n{results.count(False)} FAILED")
sys.exit(0 if all(results) else 1)
