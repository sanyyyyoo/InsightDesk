"""
Equivalence check: the app's boilerplate suppression (backend/services/boilerplate.py, refresh + strip)
must clean texts exactly like the tested E4a step (experiments/dedup/normalize.boilerplate_suppress).

Synthetic set (488 complaints, 10 generator stock phrases) must match 1:1; also reports what the rule
finds on real Play Store reviews (expected: nothing) and Firefox reports (Bugzilla template lines).
No Supabase, no Pinecone, no LLM. Needs the experiments clone at D:/PBL/InsightDesk-dedup.

  python test_boilerplate_equivalence.py
"""

import os
import sys
import tempfile
import types

import pandas as pd
from sentence_transformers import SentenceTransformer

EXP = "D:/PBL/InsightDesk-dedup"
model = SentenceTransformer("all-MiniLM-L6-v2")
sys.modules["backend.services.embedding_service"] = types.SimpleNamespace(model=model)   # no Pinecone
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(EXP, "experiments", "dedup"))
os.environ["BOILERPLATE_PATH"] = os.path.join(tempfile.mkdtemp(), "boilerplate.json")

from backend.services import boilerplate as bp  # noqa: E402
from normalize import boilerplate_suppress  # noqa: E402

failed = 0
texts = pd.read_csv(os.path.join(EXP, "data", "synthetic_ground_truth.csv")).complaint_text.astype(str).tolist()
ref = boilerplate_suppress(texts, model)
info = bp.refresh(texts)
same = sum(bp.strip(t).split() == r.split() for t, r in zip(texts, ref))
ok = same == len(texts)
failed += not ok
print(f"{'ok  ' if ok else 'FAIL'} synthetic: {same}/{len(texts)} cleaned exactly as E4a ({info['boilerplate_segments']} boilerplate segments)")
for f in ("playstore_all.csv", "firefox3.csv"):
    t = pd.read_csv(os.path.join(EXP, "data", "external", f)).complaint_text.astype(str).tolist()
    info = bp.refresh(t)
    print(f"info {f}: {info['boilerplate_segments']} boilerplate segments, {sum(bp.strip(x) != x for x in t)} of {len(t)} texts changed")
print("ALL PASSED" if not failed else f"{failed} FAILED")
sys.exit(1 if failed else 0)
