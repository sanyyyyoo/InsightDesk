"""
Live spike demo for the judges: send a burst of complaints about ONE new problem through the real pipeline
(cleaning -> retrieval -> decision band -> LLM judge) on the TEST project, then show that they were grouped into
one case and that the Poisson CUSUM flags it as a spike and makes it escalation-eligible.

  python demo_spike.py                    # 6 reports of the default problem
  python demo_spike.py --count 8          # more reports
  python demo_spike.py --problem "..."    # your own first complaint (the others are paraphrases only for the default)

Writes only to the TEST Supabase project and Pinecone index from .env.test(.txt); refuses to run against the live
project, exactly like run_test_backend.py. No email is sent (sender blanked). Each report comes from a different
demo user, because a repeat from the same user within 24 h is attached but not counted. Run it while the staging
backend and frontend are up, then open the Incidents page: the new case appears as spiking.
"""

import argparse
import contextlib
import io
import os
import sys
import time
import uuid

from dotenv import dotenv_values

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_PROJECT, LIVE_INDEX = "hziqam", "insightdesk1"

# One concrete problem, reported in different words by different customers (as in a real outage).
REPORTS = [
    "Since this morning the export to PDF button does nothing, reports never download.",
    "Exporting a report as PDF fails silently, I click export and no file is downloaded.",
    "PDF export is broken today, the download never starts when I export my report.",
    "Clicking 'Export PDF' on any report does nothing at all since the last update.",
    "Can't download reports as PDF anymore, the export button just spins and nothing happens.",
    "Report export to PDF stopped working, no file arrives after pressing export.",
    "Our team cannot export reports to PDF today, the export button is unresponsive.",
    "PDF report export not working, nothing gets downloaded when I hit export.",
]


def load_env():
    path = next((os.path.join(HERE, f) for f in (".env.test", ".env.test.txt") if os.path.exists(os.path.join(HERE, f))), None)
    if path is None:
        sys.exit("No .env.test or .env.test.txt found next to this script.")
    env = {k: (v or "").strip() for k, v in dotenv_values(path).items()}
    if not env.get("SUPABASE_KEY") and env.get("SUPABASE_SECRET_KEY"):
        env["SUPABASE_KEY"] = env["SUPABASE_SECRET_KEY"]
    if LIVE_PROJECT in env.get("SUPABASE_URL", "") or env.get("PINECONE_INDEX") == LIVE_INDEX:
        sys.exit("Refusing to run: the test file points at the LIVE project or index.")
    env.update({"EMAIL_ID": "", "EMAIL_PASSWORD": "", "SMTP_SERVER": "localhost", "SMTP_PORT": "1025",
                "DEDUP_MODE": env.get("DEDUP_MODE") or "r1", "REJOIN_ENABLED": "0", "UNASSIGNED_SPIKES": "1",
                "LLM_PROVIDER": env.get("LLM_PROVIDER") or "groq",
                "GROQ_MODEL": env.get("GROQ_MODEL") or "openai/gpt-oss-120b"})
    exp = dotenv_values(os.path.join(HERE, ".env.experiments"))
    key = next((v for k, v in exp.items() if k.startswith("GROQ_API_KEY") and v and k not in
                ("GROQ_API_KEY_3", "GROQ_API_KEY_4", "GROQ_API_KEY_12")), None)
    if key:
        env["GROQ_API_KEY"] = key.strip()
    os.environ.update(env)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=6)
    ap.add_argument("--product", default="Demo Helpdesk")
    ap.add_argument("--problem", default=None, help="text of the first complaint (default: PDF export outage)")
    ap.add_argument("--delay", type=float, default=1.5, help="seconds between reports, so the audience can follow")
    args = ap.parse_args()
    load_env()
    sys.path.insert(0, HERE)

    from fastapi.testclient import TestClient

    from backend.auth import AuthUser, get_current_user, require_admin
    from backend.main import app

    who = {"id": None}
    app.dependency_overrides[get_current_user] = lambda: AuthUser(id=who["id"], email=None, role="customer")
    app.dependency_overrides[require_admin] = lambda: AuthUser(id="demo-admin", email=None, role="admin")
    client = TestClient(app, raise_server_exceptions=False)   # no lifespan: the scheduler stays off

    texts = ([args.problem] if args.problem else []) + REPORTS
    texts = (texts * ((args.count // len(texts)) + 1))[:args.count]
    run = uuid.uuid4().hex[:6]
    print(f"\nSending {args.count} reports of one problem for product '{args.product}' (TEST project, no email)\n")
    cases = []
    for n, text in enumerate(texts, 1):
        who["id"] = f"demo-{run}-{n}"                         # a different customer each time
        with contextlib.redirect_stdout(io.StringIO()):          # hide the backend's debug prints
            r = client.post("/analyze", json={"complaint_text": text, "product": args.product})
        if r.status_code != 200:
            print(f"  [{n}] HTTP {r.status_code}: {r.text[:150]}")
            continue
        d = r.json()
        cases.append(d["case_id"])
        how = {"auto_merge": "joined automatically (similarity >= 0.8306)", "judge_merge": "joined by the LLM judge",
               "new_empty": "new case (first report)", "new_low": "new case (nothing similar)",
               "new_judge": "new case (judge: different problem)", "vague": "too vague, sent to the vague pool",
               "judge_failed": "new case (judge unavailable)"}.get(d.get("dedup_route"), d.get("status"))
        print(f"  [{n}] \"{text[:70]}\"\n       -> case {d['case_id']}: {how}")
        time.sleep(args.delay)

    if not cases:
        sys.exit("No report was processed.")
    main_case = max(set(cases), key=cases.count)
    print(f"\n{cases.count(main_case)} of {len(cases)} reports were grouped into case {main_case}.")
    with contextlib.redirect_stdout(io.StringIO()):
        info = client.get(f"/dashboard/cases/{main_case}/intelligence")
    if info.status_code == 200:
        j = info.json()
        sp, esc = j.get("spike") or {}, j.get("escalation") or {}
        print(f"Spike detected (Poisson CUSUM): {'YES' if sp.get('spike') else 'no'}"
              + (f"  - {sp.get('current')} reports in this 6-hour window against a usual {sp.get('baseline_rate')}"
                 f" per window; CUSUM score {sp.get('cusum')} (alarm at {sp.get('cusum_threshold')})" if sp else ""))
        print(f"Escalation-eligible: {'YES' if esc.get('eligible') else 'no'}"
              + (f"  ({'; '.join(esc.get('reasons') or [])})" if esc.get("reasons") else ""))
    else:
        print(f"(could not read the case summary: HTTP {info.status_code})")
    print("\nOpen the dashboard -> Incidents to see the spiking case; generate its root cause from the case page.\n")


if __name__ == "__main__":
    main()
