"""
Seed the STAGING (test) Supabase project and Pinecone index with real complaints, grouped by the final
pipeline (R1 + re-joining + unassigned-complaint alarm), for usability testing of the React frontend.

  python seed_staging.py [N]        # N most recent real (non-synthetic, non-eval) complaints, default 400

- Reads the LIVE project once, read-only (select only), to copy complaint texts and dates.
- Everything it writes goes to the test project/index from .env.test(.txt); it refuses to run if those
  point at the live project or index, exactly like run_test_backend.py.
- WIPES the test project's case/complaint tables and the test index first.
- Complaints go through the real /analyze route in time order with the app clock set to each complaint's
  date, shifted so the newest complaint lands "now" (spikes and windows then look current in the UI).
- The R1 judge uses the experiment Groq keys with rotation; answers are cached in reports/staging/llm_cache.jsonl
  so an interrupted seed restarts without repeating calls. No email can be sent.
"""

import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

from dotenv import dotenv_values

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_ENV = "D:/PBL/InsightDesk/.env"
OUT = os.path.join(HERE, "reports", "staging")
CACHE = os.path.join(OUT, "llm_cache.jsonl")
REJOIN_ONLY = "--rejoin-only" in sys.argv          # finish an interrupted seed: only the re-joining pass
N = int(next((a for a in sys.argv[1:] if a.isdigit()), 400))
MODEL = "openai/gpt-oss-120b"

# ---- 1. read the live complaints (read-only) before the test env is loaded ----
live = dotenv_values(LIVE_ENV)
from supabase import create_client  # noqa: E402

live_db = create_client(live["SUPABASE_URL"], live["SUPABASE_KEY"])
rows, s = [], 0
while True:
    page = (live_db.table("complaints").select("complaint_id,complaint_text,product,created_at,user_id,is_synthetic,rating")
            .order("complaint_id").range(s, s + 999).execute().data)
    rows += page
    s += 1000
    if len(page) < 1000:
        break
real = [r for r in rows if not r["is_synthetic"] and not (r["user_id"] or "").startswith("eval_")]
real.sort(key=lambda r: (r["created_at"], r["complaint_id"]))
real = real[-N:]
print(f"live: {len(rows)} complaints read, {len(real)} real ones selected (read-only)", flush=True)
del live_db

# ---- 2. load the TEST env (same guards as run_test_backend.py) ----
path = next((os.path.join(HERE, f) for f in (".env.test", ".env.test.txt") if os.path.exists(os.path.join(HERE, f))), None)
if path is None:
    sys.exit("No .env.test or .env.test.txt found.")
env = {k: (v or "").strip() for k, v in dotenv_values(path).items()}
if not env.get("SUPABASE_KEY") and env.get("SUPABASE_SECRET_KEY"):
    env["SUPABASE_KEY"] = env["SUPABASE_SECRET_KEY"]
if "hziqam" in env["SUPABASE_URL"] or env["PINECONE_INDEX"] == "insightdesk1" or env["SUPABASE_URL"] == live["SUPABASE_URL"]:
    sys.exit("Refusing: the test env points at the LIVE project or index.")
env.update({"EMAIL_ID": "", "EMAIL_PASSWORD": "", "SMTP_SERVER": "localhost", "SMTP_PORT": "1025",
            "DEDUP_MODE": "r1", "REJOIN_ENABLED": "1", "UNASSIGNED_SPIKES": "1",
            "LLM_PROVIDER": "groq", "GROQ_MODEL": MODEL})
os.environ.update(env)
sys.path.insert(0, HERE)

# ---- 3. app clock ----
CLOCK = [datetime.now(timezone.utc)]


class FakeDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return CLOCK[0] if tz is not None else CLOCK[0].replace(tzinfo=None)

    @classmethod
    def utcnow(cls):
        return CLOCK[0].replace(tzinfo=None)


# ---- 4. rotating Groq judge with a cache (as replay_real_data.py) ----
class GroqRotating:
    def __init__(self):
        from groq import Groq
        keys = dotenv_values(os.path.join(HERE, ".env.experiments"))
        self.clients = [Groq(api_key=v.strip()) for k, v in sorted(keys.items())
                        if k.startswith("GROQ_API_KEY") and v and k not in ("GROQ_API_KEY_3", "GROQ_API_KEY_4", "GROQ_API_KEY_12")]
        self.k, self.free_at, self.calls, self.cache = 0, [0.0] * len(self.clients), 0, {}
        if os.path.exists(CACHE):
            for line in open(CACHE, encoding="utf-8"):
                r = json.loads(line)
                self.cache[r["h"]] = r["reply"]

    def __call__(self, prompt):
        h = hashlib.sha1(prompt.encode("utf-8")).hexdigest()
        if h in self.cache:
            return self.cache[h]
        while True:
            try:
                resp = self.clients[self.k].chat.completions.create(
                    model=MODEL, temperature=0, response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}])
                reply = json.loads(resp.choices[0].message.content)
                break
            except Exception as exc:
                m = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?([\d.]+)s", str(exc))
                wait = (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + float(m.group(3)) + 5) if m else 30
                self.free_at[self.k] = time.time() + wait
                self.k = min(range(len(self.clients)), key=lambda j: self.free_at[j])
                pause = max(0.0, self.free_at[self.k] - time.time())
                print(f"[groq] rotating to key {self.k + 1}" + (f", sleeping {pause:.0f}s" if pause else ""), flush=True)
                time.sleep(pause)
        self.cache[h] = reply
        self.calls += 1
        with open(CACHE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"h": h, "reply": reply}) + "\n")
        return reply


def wipe(db):
    for table, pk in (("case_rca", "rca_id"), ("case_history", "history_id"), ("complaint_windows", "window_id"),
                      ("complaints", "complaint_id"), ("cases", "case_id"), ("topics", "topic_id")):
        try:
            db.table(table).delete().neq(pk, -1).execute()
        except Exception as exc:
            print(f"  wipe {table}: {str(exc)[:80]}", flush=True)
    from pinecone import Pinecone
    idx = Pinecone(api_key=env["PINECONE_API_KEY"]).Index(env["PINECONE_INDEX"])
    try:
        idx.delete(delete_all=True)
    except Exception as exc:                       # empty index raises "namespace not found"
        print(f"  wipe index: {str(exc)[:80]}", flush=True)
    print("test project and index wiped", flush=True)


def main():
    os.makedirs(OUT, exist_ok=True)
    from fastapi.testclient import TestClient

    import backend.database.supabase as supa
    import backend.llm.provider as provider
    import backend.services.duplicate_service as dup
    import backend.services.rca_service as rca
    from backend.auth import AuthUser, get_current_user
    from backend.main import app

    for mod in (supa, dup, rca):
        if hasattr(mod, "datetime"):
            mod.datetime = FakeDateTime
    import backend.routers.complaints as complaints_router
    complaints_router.WEB_PORTAL_SOURCE = "google_play_store"   # these are Play Store reviews: short-text t_low 0.40
    llm = GroqRotating()
    provider.generate_json = llm
    if REJOIN_ONLY:
        client = TestClient(app, raise_server_exceptions=False)
        rj = client.post("/dashboard/rejoin")
        print(f"re-joining pass: HTTP {rj.status_code} {rj.text[:300]}", flush=True)
        open(os.path.join(OUT, "seed_summary.txt"), "a", encoding="utf-8").write(f"rejoin-only: {rj.text[:300]}\n")
        return
    wipe(supa.supabase)

    def ts(r):
        return datetime.fromisoformat(str(r["created_at"]).replace("Z", "+00:00")).replace(tzinfo=timezone.utc)
    shift = datetime.now(timezone.utc) - ts(real[-1])
    who = {}
    app.dependency_overrides[get_current_user] = lambda: AuthUser(id=who["id"], email=None, role="customer")
    client = TestClient(app, raise_server_exceptions=False)
    t0, ok, fail = time.time(), 0, 0
    for n, r in enumerate(real):
        when = ts(r) + shift
        CLOCK[0] = when
        who["id"] = f"staging-{r['complaint_id']}"            # the source has one shared user id for all reviews
        body = {"complaint_text": r["complaint_text"], "product": r["product"]}
        if r.get("rating"):
            body["rating"] = int(r["rating"])
        res = client.post("/analyze", json=body)
        if res.status_code == 200:
            ok += 1
            cid = (res.json() or {}).get("complaint_id")
            if cid:                                          # stored at the shifted original time
                supa.supabase.table("complaints").update({"created_at": when.isoformat()}).eq("complaint_id", cid).execute()
        else:
            fail += 1
            print(f"  {n}: HTTP {res.status_code} {res.text[:120]}", flush=True)
        if (n + 1) % 25 == 0:
            print(f"{n + 1}/{len(real)} complaints, {llm.calls} new LLM calls, {time.time() - t0:.0f}s", flush=True)
    # case created_at = its first complaint (the table default stamped the real wall clock)
    comps = supa._select_all("complaints", "complaint_id", "case_id,created_at")
    first = {}
    for c in comps:
        if c["case_id"] is not None and (c["case_id"] not in first or c["created_at"] < first[c["case_id"]]):
            first[c["case_id"]] = c["created_at"]
    for case_id, t in first.items():
        supa.supabase.table("cases").update({"created_at": t}).eq("case_id", case_id).execute()
    CLOCK[0] = datetime.now(timezone.utc)
    rj = client.post("/dashboard/rejoin")
    print(f"re-joining pass: HTTP {rj.status_code} {rj.text[:200]}", flush=True)
    summary = f"seeded {ok} complaints ({fail} failed), {len(first)} cases, {llm.calls} new LLM calls, rejoin: {rj.text[:200]}"
    print(summary, flush=True)
    open(os.path.join(OUT, "seed_summary.txt"), "w", encoding="utf-8").write(summary + "\n")


if __name__ == "__main__":
    main()
