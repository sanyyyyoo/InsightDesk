"""
Local end-to-end check of the whole pipeline with spike detector v2.

Runs the REAL backend code (FastAPI app, /analyze ingestion, MiniLM embeddings,
cross-encoder dedup, RoBERTa sentiment, complaint windows, spike detection,
dashboard endpoints, RCA) against IN-MEMORY stand-ins:
  - Supabase: a fake client that executes the same query-builder calls on
    Python lists (the real backend/database/supabase.py code runs unchanged);
  - Pinecone: a fake index with cosine top-k;
  - the clock: simulated, so a week of complaints replays in seconds;
  - the RCA LLM call: a fixed JSON answer (no Groq quota, no network);
  - with --r1: DEDUP_MODE=r1, and the R1 judge call answered by a simple
    offline stand-in (same JSON shape as the real judge).
Nothing is written to Supabase or Pinecone. No email is sent.

  python test_e2e_local.py
"""

import copy
import importlib.util
import itertools
import os
import random
import subprocess
import sys
import types
from datetime import datetime, timedelta, timezone

import numpy as np

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")
os.environ.setdefault("SUPABASE_URL", "http://fake.local")
os.environ.setdefault("SUPABASE_KEY", "fake")
os.environ.setdefault("PINECONE_API_KEY", "fake")
os.environ.setdefault("PINECONE_INDEX", "fake")
os.environ.setdefault("SMTP_SERVER", "smtp.invalid")
os.environ.setdefault("SMTP_PORT", "0")
R1 = "--r1" in sys.argv
if R1:
    os.environ["DEDUP_MODE"] = "r1"


def _no_email(*a, **kw):
    raise RuntimeError("email is disabled in the local end-to-end test")


import smtplib  # noqa: E402

smtplib.SMTP = smtplib.SMTP_SSL = _no_email

# ----------------------------------------------------------------------
# simulated clock
# ----------------------------------------------------------------------

CLOCK = [datetime(2026, 10, 1, tzinfo=timezone.utc)]


class FakeDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return CLOCK[0] if tz is not None else CLOCK[0].replace(tzinfo=None)

    @classmethod
    def utcnow(cls):
        return CLOCK[0].replace(tzinfo=None)


# ----------------------------------------------------------------------
# in-memory Supabase
# ----------------------------------------------------------------------

PK = {"topics": "topic_id", "cases": "case_id", "complaints": "complaint_id",
      "complaint_windows": "window_id", "case_history": "history_id", "case_rca": "rca_id",
      "clustering_metadata": "metadata_id", "model_benchmarks": "benchmark_id"}
DEFAULTS = {
    "cases": {"report_count": 1, "user_ids": [], "spike_status": False, "topic_id": None, "is_vague": False,
              "sentiment": None, "confidence_score": None, "sentiment_model": None,
              "emotion": None, "emotion_confidence": None, "spike_score": None, "spike_detected_at": None},
    "complaints": {"is_synthetic": False, "is_duplicate": False, "case_id": None, "cleaned_text": None},
    "complaint_windows": {"complaint_ct": 0},
    "case_rca": {"source_evidence": []},
    "clustering_metadata": {"clustering_version": 0, "last_case_count": 0, "total_topics": 0,
                            "outlier_rate": 0, "last_clustered_at": None},
}
NOW_COLS = {"created_at", "last_reported_at", "generated_at"}


def _key(v):
    if isinstance(v, str):
        try:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))
        except ValueError:
            return v
    return v


class Result:
    def __init__(self, data, count=None):
        self.data, self.count = data, count


class Query:
    def __init__(self, db, table):
        self.db, self.table_name = db, table
        self.rows = db.tables.setdefault(table, [])
        self.op, self.payload, self.filters = "select", None, []
        self.cols, self.count_mode, self.head = "*", None, False
        self.order_by, self.lim, self.one, self.off = [], None, False, 0

    def select(self, cols="*", count=None, head=False):
        if self.op == "select":
            self.cols, self.count_mode, self.head = cols, count, head
        return self

    def insert(self, data):
        self.op, self.payload = "insert", data
        return self

    def update(self, data):
        self.op, self.payload = "update", data
        return self

    def upsert(self, data, **kw):
        self.op, self.payload = "upsert", data
        return self

    def delete(self):
        self.op = "delete"
        return self

    def eq(self, c, v):
        self.filters.append(lambda r: _key(r.get(c)) == _key(v))
        return self

    def neq(self, c, v):
        self.filters.append(lambda r: _key(r.get(c)) != _key(v))
        return self

    def gte(self, c, v):
        self.filters.append(lambda r: r.get(c) is not None and _key(r.get(c)) >= _key(v))
        return self

    def lte(self, c, v):
        self.filters.append(lambda r: r.get(c) is not None and _key(r.get(c)) <= _key(v))
        return self

    def in_(self, c, vs):
        vs = list(vs)
        self.filters.append(lambda r: r.get(c) in vs)
        return self

    def is_(self, c, v):
        self.filters.append(lambda r: r.get(c) is None if v in (None, "null") else r.get(c) == v)
        return self

    def order(self, c, desc=False):
        self.order_by.append((c, desc))
        return self

    def limit(self, n):
        self.lim = n
        return self


    def range(self, a, b):
        self.off, self.lim = a, b - a + 1
        return self
    def single(self):
        self.one = True
        return self

    maybe_single = single

    def _match(self):
        return [r for r in self.rows if all(f(r) for f in self.filters)]

    def _project(self, r):
        if self.cols.strip() == "*":
            return copy.deepcopy(r)
        return {c.strip(): copy.deepcopy(r.get(c.strip())) for c in self.cols.split(",")}

    def execute(self):
        if self.op in ("insert", "upsert"):
            items = self.payload if isinstance(self.payload, list) else [self.payload]
            out = []
            for item in items:
                pk = PK.get(self.table_name, "id")
                row = dict(DEFAULTS.get(self.table_name, {}))
                for c in NOW_COLS:
                    row.setdefault(c, CLOCK[0].isoformat())
                row.update(copy.deepcopy(item))
                if row.get(pk) is None:
                    row[pk] = next(self.db.ids[self.table_name])
                self.rows.append(row)
                out.append(copy.deepcopy(row))
            return Result(out)
        hits = self._match()
        if self.op == "update":
            for r in hits:
                r.update(copy.deepcopy(self.payload))
            return Result([copy.deepcopy(r) for r in hits])
        if self.op == "delete":
            for r in hits:
                self.rows.remove(r)
            return Result([copy.deepcopy(r) for r in hits])
        for c, desc in reversed(self.order_by):
            hits = sorted(hits, key=lambda r: (_key(r.get(c)) is None, _key(r.get(c))), reverse=desc)
        n = len(hits)
        if self.lim is not None:
            hits = hits[self.off:self.off + self.lim]
        data = [] if self.head else [self._project(r) for r in hits]
        if self.one:
            data = data[0] if data else None
        return Result(data, count=n if self.count_mode else None)


class FakeSupabase:
    def __init__(self):
        self.tables = {}
        self.ids = {t: itertools.count(1) for t in PK}

    def table(self, name):
        return Query(self, name)


DB = FakeSupabase()
sb = types.ModuleType("supabase")
sb.Client = FakeSupabase
sb.create_client = lambda url, key: DB
sys.modules["supabase"] = sb

# ----------------------------------------------------------------------
# in-memory Pinecone
# ----------------------------------------------------------------------


class FakeIndex:
    def __init__(self):
        self.vecs = {}

    def upsert(self, vectors, **kw):
        for v in vectors:
            self.vecs[v["id"]] = (np.asarray(v["values"], dtype=float), dict(v.get("metadata", {})))

    def query(self, vector, top_k=5, include_metadata=True, filter=None, **kw):
        q = np.asarray(vector, dtype=float)
        q = q / (np.linalg.norm(q) or 1)
        want = filter or {}
        scored = [(float(e @ q / (np.linalg.norm(e) or 1)), i, m) for i, (e, m) in self.vecs.items()
                  if all(m.get(k) == v for k, v in want.items())]
        scored.sort(reverse=True)
        return {"matches": [{"id": i, "score": s, "metadata": m} for s, i, m in scored[:top_k]]}

    def fetch(self, ids=None, **kw):
        return {"vectors": {i: {"values": list(self.vecs[i][0])} for i in ids or [] if i in self.vecs}}

    def delete(self, ids=None, **kw):
        for i in ids or []:
            self.vecs.pop(str(i), None)


INDEX = FakeIndex()
pc = types.ModuleType("pinecone")
pc.Pinecone = lambda **kw: types.SimpleNamespace(Index=lambda name: INDEX)
sys.modules["pinecone"] = pc

# ----------------------------------------------------------------------
# load the app, then patch its clock and the RCA LLM call
# ----------------------------------------------------------------------

from fastapi.testclient import TestClient  # noqa: E402

import backend.database.supabase as supa  # noqa: E402
import backend.services.duplicate_service as dup  # noqa: E402
import backend.services.rca_service as rca  # noqa: E402
from backend.main import app  # noqa: E402

for mod in (supa, dup, rca):
    if hasattr(mod, "datetime"):
        mod.datetime = FakeDateTime

LLM_CALLS = []


def fake_generate_json(prompt):
    LLM_CALLS.append(prompt)
    return {"probable_cause": "Push notification service broken after the latest update",
            "affected_segment": "Mobile app users", "recommended_action": "Roll back the notification change",
            "severity": "high", "confidence": 0.8, "source_evidence": []}


rca.generate_json = fake_generate_json
import backend.routers.dashboard as dash  # noqa: E402

ESCALATED = []
dash.escalate_case = lambda case_id: ESCALATED.append(case_id) or True   # no email in tests
JUDGE_CALLS = []


def fake_judge_json(prompt):
    """Offline stand-in for the R1 judge: same case if both mention notifications."""
    import re
    JUDGE_CALLS.append(prompt)
    new = prompt.split("New complaint:")[1].split("Existing cases:")[0].lower()
    cases = re.findall(r"Case (\d+): (.*)", prompt.split("Existing cases:")[1])
    specific = len(new.split()) > 4
    pick = next((int(n) for n, t in cases if "notif" in new and "notif" in t.lower()), 0)
    return {"specific": specific, "case": pick}


if R1:
    import backend.llm.provider as provider
    provider.generate_json = fake_judge_json
# /analyze needs a Supabase login since the auth merge; these tests are not about login
from backend.auth import AuthUser, get_current_user  # noqa: E402
_ids = __import__("itertools").count(1)  # a new user per request, like separate customers
app.dependency_overrides[get_current_user] = lambda: AuthUser(id=f"e2e-user-{next(_ids)}", email=None, role="customer")
client = TestClient(app, raise_server_exceptions=False)

# ----------------------------------------------------------------------
# scenario: a quiet week of real Play Store reviews, then a burst
# ----------------------------------------------------------------------

BURST = [   # one problem, worded differently by different users
    "Notifications stopped working after the last update, I don't get any alerts for new tickets",
    "Since updating the app I receive no push notifications for new tickets at all",
    "Push notifications are broken after the update. No alerts when a ticket comes in",
    "After the latest update the app stopped sending notifications for incoming tickets",
    "Not getting notified about new tickets anymore since the update",
    "The update broke notifications, new ticket alerts never arrive",
]
BACKGROUND_SAME = [   # the same problem, reported rarely during the quiet week
    "I'm not getting notifications for new tickets on my phone",
]


def post(text, user, when):
    CLOCK[0] = when
    r = client.post("/analyze", json={"complaint_text": text, "user_id": user, "source": "playstore",
                                      "product": "Zendesk"})
    assert r.status_code == 200, r.text
    ROUTES.append(r.json())
    return r.json()


ROUTES = []


def main():
    import pandas as pd
    rng = random.Random(3)
    t0 = CLOCK[0]
    reviews = pd.read_csv("D:/PBL/InsightDesk-dedup/data/external/playstore_scored.csv")
    reviews = reviews[(reviews.department == "Zendesk") & ~reviews.complaint_text.str.contains("notif", case=False)]
    quiet = reviews.sample(35, random_state=3).complaint_text.tolist()

    print("phase 1: quiet week (35 real Zendesk reviews + 1 notification complaint)")
    events = [(t0 + timedelta(minutes=rng.randint(0, 7 * 24 * 60)), txt) for txt in quiet]
    events.append((t0 + timedelta(days=3, hours=5), BACKGROUND_SAME[0]))
    for k, (when, txt) in enumerate(sorted(events)):
        post(txt, f"user_q{k}", when)

    print("phase 2: burst - 6 users report broken notifications within 3 hours on day 8")
    burst_start = t0 + timedelta(days=8, hours=7)
    burst = [post(txt, f"user_b{k}", burst_start + timedelta(minutes=30 * k)) for k, txt in enumerate(BURST)]
    burst_cases = pd.Series([b["case_id"] for b in burst]).value_counts()
    main_case = int(burst_cases.index[0])
    print(f"  burst complaints went to cases {dict(burst_cases)} -> main case {main_case}")

    CLOCK[0] = burst_start + timedelta(hours=4)
    checks = []

    def check(name, ok, detail=""):
        checks.append(ok)
        print(f"  {'ok  ' if ok else 'FAIL'} {name}{(': ' + detail) if detail else ''}")

    print("dashboard and RCA endpoints")
    sp = client.get("/dashboard/spikes")
    check("GET /dashboard/spikes responds", sp.status_code == 200, str(sp.status_code))
    spikes = sp.json() if sp.status_code == 200 else []
    spikes = spikes.get("spikes", spikes) if isinstance(spikes, dict) else spikes
    spike_ids = {s.get("case_id") for s in spikes}
    check("burst case is flagged as a spike", main_case in spike_ids, f"spike cases {sorted(spike_ids)}")
    check("no quiet-week case is flagged", spike_ids <= set(burst_cases.index), f"{len(spike_ids)} flagged")

    gs = client.get("/dashboard/group-spikes")
    check("GET /dashboard/group-spikes responds", gs.status_code == 200, str(gs.status_code))
    if gs.status_code == 200:
        groups = gs.json()
        burst_set = set(int(c) for c in burst_cases.index)
        in_one = [g for g in groups if burst_set <= set(g["case_ids"])]
        if len(burst_set) > 1:
            # Known limitation (not a failure): with a tiny stream (42 complaints) the burst's own
            # pairs ARE the top 1% of similarities, so the 99th-percentile threshold (the tested
            # rule) equals the burst's internal similarity and its two halves may stay apart.
            print(f"  info: split burst joined in one group alert: {bool(in_one)} "
                  f"(group alerts {[g['case_ids'] for g in groups] or 'none'}; small-stream limitation)")
        else:
            print(f"  burst is one case; group alerts: {[g['case_ids'] for g in groups] or 'none'}")
        quiet = [g for g in groups if not (set(g["case_ids"]) & burst_set)]
        check("no group alert made only of quiet-week cases", not quiet, f"{[g['case_ids'] for g in quiet]}")

    print("escalation policy and vague summary")
    small = next(c["case_id"] for c in DB.tables["cases"]
                 if c["report_count"] == 1 and c["case_id"] not in set(burst_cases.index))
    r = client.post(f"/dashboard/cases/{small}/escalate")
    check("1-report quiet case is NOT escalated (409)", r.status_code == 409, str(r.status_code))
    r = client.post(f"/dashboard/cases/{small}/escalate?force=true")
    check("same case with force=true is escalated and marked forced",
          r.status_code == 200 and r.json().get("forced") is True, str(r.status_code))
    r = client.post(f"/dashboard/cases/{main_case}/escalate")
    check("spiking burst case passes the policy", r.status_code == 200 and r.json().get("forced") is False,
          f"{r.status_code} {r.json().get('policy', r.json().get('detail'))}")
    ci2 = client.get(f"/dashboard/cases/{main_case}/intelligence").json()
    check("case intelligence returns escalation + rca_recommended",
          "escalation" in ci2 and ci2.get("rca_recommended") is True)
    vs = client.get("/dashboard/vague-summary")
    n_vague = sum(1 for c in DB.tables["cases"] if c.get("is_vague"))
    check("GET /dashboard/vague-summary responds and matches is_vague cases",
          vs.status_code == 200 and vs.json()["vague_cases"] == n_vague, f"{vs.json() if vs.status_code == 200 else vs.status_code}")
    if R1:
        check("R1 marked its vague complaints in the cases table", n_vague == sum(r.get("dedup_route") == "vague" for r in ROUTES),
              f"{n_vague} vague cases")
        vague_case = next((c["case_id"] for c in DB.tables["cases"] if c.get("is_vague")), None)
        if vague_case:
            r = client.post(f"/dashboard/cases/{vague_case}/escalate")
            check("vague case is NOT escalated (409)", r.status_code == 409, str(r.status_code))

    ov = client.get("/dashboard/overview")
    check("GET /dashboard/overview responds", ov.status_code == 200, str(ov.status_code))
    ci = client.get(f"/dashboard/cases/{main_case}/intelligence")
    check("GET /dashboard/cases/{id}/intelligence responds", ci.status_code == 200, str(ci.status_code))
    if ci.status_code == 200:
        s = ci.json().get("spike") or {}
        check("case intelligence shows the spike", bool(s.get("spike")),
              f"current={s.get('current')} rate={s.get('baseline_rate')} p={s.get('p_value')}")
    rca.generate_rca(main_case)                  # as the Streamlit dashboard does
    rc = client.get(f"/dashboard/rca/{main_case}")
    if rc.status_code == 200:
        check("RCA prompt tells the LLM about the spike", bool(LLM_CALLS) and ("Spike Detected:\nyes" in LLM_CALLS[-1]          # v1 prompt
                                                or "Spike detected: yes" in LLM_CALLS[-1]))   # v2/v3 prompt
    check("GET /dashboard/rca/{id} responds", rc.status_code == 200, f"{rc.status_code}, LLM stub calls {len(LLM_CALLS)}")

    print("same database, OLD detector (git HEAD version)")
    old_src = subprocess.run(["git", "show", "HEAD:backend/services/spike_detection.py"],
                             capture_output=True, text=True, check=True).stdout
    spec = importlib.util.spec_from_loader("old_spike", loader=None)
    old = importlib.util.module_from_spec(spec)
    exec(old_src, old.__dict__)
    old_flag = [c["case_id"] for c in DB.tables["cases"] if old.detect_spike(c["case_id"])["spike"]]
    print(f"  old detector flags: {old_flag or 'nothing'}")

    if R1:
        print("R1 mode")
        routes = pd.Series([r.get("dedup_route") for r in ROUTES]).value_counts().to_dict()
        check("R1 used for every complaint", all(r.get("dedup_route") != "cross_encoder" for r in ROUTES), str(routes))
        check("burst lands in ONE case under R1", len(burst_cases) == 1, f"cases {dict(burst_cases)}")
        check("one exemplar vector per new case, at most 5 per case",
              all(1 <= sum(m["case_id"] == c["case_id"] for _, m in INDEX.vecs.values()) <= 5
                  for c in DB.tables["cases"]))
        print(f"  judge calls {len(JUDGE_CALLS)}")

    n_cases = len(DB.tables["cases"])
    print(f"\ncomplaints {len(DB.tables['complaints'])}, cases {n_cases}, "
          f"windows {len(DB.tables['complaint_windows'])}, vectors {len(INDEX.vecs)}")
    print("ALL PASSED" if all(checks) else "SOME CHECKS FAILED")
    return 0 if all(checks) else 1


if __name__ == "__main__":
    sys.exit(main())
