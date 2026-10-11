"""
Real-services test: the same scenario as test_e2e_local.py, but against a REAL
test Supabase project and a REAL test Pinecone index (from this clone's .env),
with the real Groq judge and RCA. Only the clock is simulated (a week of
complaints in minutes) and email is blocked.

Safety (the script stops before writing anything if any check fails):
  - SUPABASE_URL / PINECONE_INDEX must differ from the live project's values
    in D:/PBL/InsightDesk/.env;
  - the test database must be empty (no cases, no complaints);
  - the cases table must have the is_vague column (schema.sql was run).
Nothing is deleted afterwards: inspect the data, then drop the test project.

  python test_real_services.py
"""

import os
import random
import sys
import time
from datetime import datetime, timedelta, timezone

from dotenv import dotenv_values, load_dotenv

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_ENV = "D:/PBL/InsightDesk/.env"
os.environ["DEDUP_MODE"] = "r1"
load_dotenv(os.path.join(HERE, ".env"), override=True)
os.environ.setdefault("HF_HUB_OFFLINE", "1")


def fail(msg):
    print("STOP:", msg)
    sys.exit(2)


test = {k: os.getenv(k) for k in ("SUPABASE_URL", "SUPABASE_KEY", "PINECONE_API_KEY", "PINECONE_INDEX", "GROQ_API_KEY")}
missing = [k for k, v in test.items() if not v or v.startswith("<")]
if missing:
    fail(f"fill these in {os.path.join(HERE, '.env')}: {missing}")
live = dotenv_values(LIVE_ENV) if os.path.exists(LIVE_ENV) else {}
if live.get("SUPABASE_URL") and live["SUPABASE_URL"].rstrip("/") == test["SUPABASE_URL"].rstrip("/"):
    fail("SUPABASE_URL is the LIVE project. Use a separate test project.")
if live.get("PINECONE_INDEX") and live["PINECONE_INDEX"] == test["PINECONE_INDEX"]:
    fail("PINECONE_INDEX is the LIVE index. Use a separate test index.")


def _no_email(*a, **kw):
    raise RuntimeError("email is disabled in this test")


import smtplib  # noqa: E402

smtplib.SMTP = smtplib.SMTP_SSL = _no_email

import backend.database.supabase as supa  # noqa: E402

db = supa.supabase
if (db.table("cases").select("case_id").limit(1).execute().data
        or db.table("complaints").select("complaint_id").limit(1).execute().data):
    fail("the test database is not empty; use a fresh test project (this script never deletes data)")
try:
    db.table("cases").select("is_vague").limit(1).execute()
except Exception as exc:
    fail(f"cases.is_vague missing - run backend/database/schema.sql in the test project first ({exc})")

from fastapi.testclient import TestClient  # noqa: E402

import backend.routers.dashboard as dash  # noqa: E402
import backend.services.duplicate_service as dup  # noqa: E402
import backend.services.rca_service as rca  # noqa: E402
from backend.main import app  # noqa: E402
from backend.services.embedding_service import index  # noqa: E402

CLOCK = [datetime.now(timezone.utc).replace(microsecond=0) - timedelta(days=9)]


class FakeDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return CLOCK[0] if tz is not None else CLOCK[0].replace(tzinfo=None)


for mod in (supa, dup, rca):
    if hasattr(mod, "datetime"):
        mod.datetime = FakeDateTime
ESCALATED = []
dash.escalate_case = lambda case_id: ESCALATED.append(case_id) or True     # policy is tested, no email
client = TestClient(app)

BURST = [
    "Notifications stopped working after the last update, I don't get any alerts for new tickets",
    "Since updating the app I receive no push notifications for new tickets at all",
    "Push notifications are broken after the update. No alerts when a ticket comes in",
    "After the latest update the app stopped sending notifications for incoming tickets",
    "Not getting notified about new tickets anymore since the update",
    "The update broke notifications, new ticket alerts never arrive",
]
CHECKS = []


def check(name, ok, detail=""):
    CHECKS.append(ok)
    print(f"  {'ok  ' if ok else 'FAIL'} {name}{(': ' + detail) if detail else ''}", flush=True)


def post(text, user, when, pause):
    CLOCK[0] = when
    r = client.post("/analyze", json={"complaint_text": text, "user_id": user, "source": "playstore", "product": "Zendesk"})
    assert r.status_code == 200, r.text
    time.sleep(pause)                       # Pinecone serverless needs a moment before new vectors are searchable
    return r.json()


def main():
    import pandas as pd
    pause = float(os.getenv("REAL_TEST_PAUSE", "2"))
    rng = random.Random(3)
    t0 = CLOCK[0]
    reviews = pd.read_csv("D:/PBL/InsightDesk-dedup/data/external/playstore_scored.csv")
    reviews = reviews[(reviews.department == "Zendesk") & ~reviews.complaint_text.str.contains("notif", case=False)]
    quiet = reviews.sample(35, random_state=3).complaint_text.tolist()
    print(f"phase 1: quiet week (35 real Zendesk reviews + 1 notification complaint), {pause}s pause per complaint")
    events = [(t0 + timedelta(minutes=rng.randint(0, 7 * 24 * 60)), t) for t in quiet]
    events.append((t0 + timedelta(days=3, hours=5), "I'm not getting notifications for new tickets on my phone"))
    routes = [post(t, f"user_q{k}", w, pause) for k, (w, t) in enumerate(sorted(events))]
    print("phase 2: burst - 6 users report broken notifications within 3 hours on day 8")
    bs = t0 + timedelta(days=8, hours=7)
    burst = [post(t, f"user_b{k}", bs + timedelta(minutes=30 * k), pause) for k, t in enumerate(BURST)]
    routes += burst
    burst_cases = pd.Series([b["case_id"] for b in burst]).value_counts()
    main_case = int(burst_cases.index[0])
    print(f"  routes: {pd.Series([r.get('dedup_route') for r in routes]).value_counts().to_dict()}")
    print(f"  burst complaints went to cases {dict(burst_cases)}")
    CLOCK[0] = bs + timedelta(hours=4)

    print("real database and vector index")
    cases = db.table("cases").select("*").execute().data
    windows = db.table("complaint_windows").select("*").execute().data
    check("one row per complaint in complaints", len(db.table("complaints").select("complaint_id").execute().data) == 42)
    check("complaint_windows: one row per (case, window)",
          len(windows) == len({(w["case_id"], w["window_start"]) for w in windows}))
    stats = index.describe_index_stats()
    n_vec = stats.get("total_vector_count") if isinstance(stats, dict) else stats.total_vector_count
    check("Pinecone holds the exemplar vectors (1-5 per case)", len(cases) <= n_vec <= 5 * len(cases),
          f"{n_vec} vectors for {len(cases)} cases")
    fetched = index.fetch(ids=[f"{main_case}:0"])
    vecs = fetched.get("vectors", {}) if isinstance(fetched, dict) else fetched.vectors
    check("burst case's first exemplar is stored with founder text", f"{main_case}:0" in vecs)
    check("vague complaints marked in cases.is_vague",
          sum(1 for c in cases if c.get("is_vague")) == sum(r.get("dedup_route") == "vague" for r in routes),
          f"{sum(1 for c in cases if c.get('is_vague'))} vague")

    print("dashboard, spikes, escalation, RCA")
    sp = client.get("/dashboard/spikes").json()
    check("burst case flagged as a spike", main_case in {s["case_id"] for s in sp}, f"spike cases {[s['case_id'] for s in sp]}")
    check("GET /dashboard/group-spikes responds", client.get("/dashboard/group-spikes").status_code == 200)
    check("GET /dashboard/overview responds", client.get("/dashboard/overview").status_code == 200)
    ci = client.get(f"/dashboard/cases/{main_case}/intelligence")
    check("case intelligence responds with escalation info", ci.status_code == 200 and "escalation" in ci.json())
    small = next(c["case_id"] for c in cases if c["report_count"] == 1 and c["case_id"] not in set(burst_cases.index))
    check("1-report case is not escalated (409)", client.post(f"/dashboard/cases/{small}/escalate").status_code == 409)
    check("spiking case passes the escalation policy", client.post(f"/dashboard/cases/{main_case}/escalate").status_code == 200)
    try:
        rca.generate_rca(main_case, force_regenerate=True)
        rr = client.get(f"/dashboard/rca/{main_case}")
        check("real RCA generated and stored", rr.status_code == 200, (rr.json().get("probable_cause") or "")[:100])
    except Exception as exc:
        check("real RCA generated and stored", False, str(exc)[:150])
    vs = client.get("/dashboard/vague-summary")
    check("vague summary responds", vs.status_code == 200, str(vs.json())[:120])
    print("ALL PASSED" if all(CHECKS) else "SOME CHECKS FAILED")
    print("Data left in the test project for inspection; delete the test project/index when done.")
    return 0 if all(CHECKS) else 1


if __name__ == "__main__":
    sys.exit(main())
