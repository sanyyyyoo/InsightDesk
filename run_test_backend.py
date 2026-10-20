"""
Start the backend against the TEST Supabase project and Pinecone index (for the Postman collection).

Reads .env.test (or .env.test.txt) from this folder, refuses to start if it points at the live
project, maps SUPABASE_SECRET_KEY to the SUPABASE_KEY the app reads, and makes email impossible
(blank sender, dummy local SMTP). Values are never printed.

  python run_test_backend.py            # http://127.0.0.1:8000 (Postman: re-joining off)
  python run_test_backend.py --staging  # final pipeline for usability testing: re-joining on
"""

import os
import sys

from dotenv import dotenv_values

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_PROJECT = "hziqam"            # the live Supabase project: never test against it
LIVE_INDEX = "insightdesk1"

path = next((os.path.join(HERE, f) for f in (".env.test", ".env.test.txt") if os.path.exists(os.path.join(HERE, f))), None)
if path is None:
    sys.exit("No .env.test or .env.test.txt found next to this script.")
env = {k: (v or "").strip() for k, v in dotenv_values(path).items()}
if not env.get("SUPABASE_KEY") and env.get("SUPABASE_SECRET_KEY"):
    env["SUPABASE_KEY"] = env["SUPABASE_SECRET_KEY"]

missing = [k for k in ("SUPABASE_URL", "SUPABASE_KEY", "PINECONE_API_KEY", "PINECONE_INDEX") if not env.get(k)]
if missing:
    sys.exit(f"Missing in {os.path.basename(path)}: {', '.join(missing)}")
if LIVE_PROJECT in env["SUPABASE_URL"] or env["PINECONE_INDEX"] == LIVE_INDEX:
    sys.exit("Refusing to start: the test file points at the LIVE project or index.")

env.update({
    "EMAIL_ID": "", "EMAIL_PASSWORD": "",          # no sender: escalation emails cannot be sent
    "SMTP_SERVER": "localhost", "SMTP_PORT": "1025",
    "DEDUP_MODE": env.get("DEDUP_MODE") or "r1",   # the current pipeline
    "REJOIN_ENABLED": "1" if "--staging" in sys.argv else "0",   # Postman checks the disabled path
    "UNASSIGNED_SPIKES": "1",                      # read-only alarm on, so its endpoint is exercised
    "ADMIN_AUTH_REQUIRED": "1" if "--staging" in sys.argv else "0",   # staging: only admin accounts reach the dashboard
    "LLM_PROVIDER": env.get("LLM_PROVIDER") or "groq",
    "GROQ_MODEL": env.get("GROQ_MODEL") or "openai/gpt-oss-120b",
})
if "--staging" in sys.argv:                         # the test project's own Groq key is invalid: use an experiment key
    exp = dotenv_values(os.path.join(HERE, ".env.experiments"))
    key = next((v for k, v in exp.items() if k.startswith("GROQ_API_KEY") and v), None)
    if key:
        env["GROQ_API_KEY"] = key.strip()
os.environ.update(env)                             # set before the app's load_dotenv() calls, which never override
print(f"Using {os.path.basename(path)}: test project, index {env['PINECONE_INDEX']}, DEDUP_MODE={env['DEDUP_MODE']}, email disabled")

import uvicorn  # noqa: E402

sys.path.insert(0, HERE)
uvicorn.run("backend.main:app", host="127.0.0.1", port=8000)
