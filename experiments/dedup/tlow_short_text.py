"""t_low 0.40 for short-text channels, tested on the unseen apps (rule: results/tlow_short_text_rule.md)."""
import glob
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e5_three_way as e5  # noqa: E402
import new_apps_score as ns  # noqa: E402
from ci_bootstrap import counts, prf  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from sentence_transformers import SentenceTransformer  # noqa: E402

sx, sy = sorted(glob.glob(os.path.join(ns.NA, "sheetX_*.xlsx")))[0], sorted(glob.glob(os.path.join(ns.NA, "sheetY_*.xlsx")))[0]
kx, _ = ns.key(sx)
ky, _ = ns.key(sy)
agreed = ns.agreed(kx, ky)                        # agreed key, indexed by sheet id

enc = SentenceTransformer(e5.EMBED_MODEL)
e5.MAX_CANDIDATES = 5
cal = load_ground_truth(path=DATA_PATHS["playstore"])
tgt = load_ground_truth(path=DATA_PATHS["new_apps"])
sheet_of = dict(zip(tgt["complaint_ref"] + e5.EXT_REF_OFFSET, tgt["sheet_id"]))
tgt["complaint_ref"] = tgt["complaint_ref"] + e5.EXT_REF_OFFSET
cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
raw = pd.concat([cal[cols].assign(_cal=True), tgt[cols].assign(_cal=False)], ignore_index=True)
df = apply_text_mode(raw, "boilerplate", enc)
texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
issues = np.array(df["issue_id"].astype(str).tolist())
groups = np.array(df["department"].astype(str).tolist())
refs = df["complaint_ref"].values
test = np.where(~df["_cal"].to_numpy(dtype=bool))[0]
truth = np.array([str(agreed[int(sheet_of[refs[i]])]) for i in test])

out = ["T_LOW 0.40 ON UNSEEN SHORT REVIEWS (rule results/tlow_short_text_rule.md): 588 unseen-app reviews, agreed LLM key"]
res = {}
for tl in (0.26, 0.40):
    judge = e5.LLMJudge(texts, refs, "new_apps_ext_playstore", "founder", "gated")
    labels, banded, _ = e5.by_group(lambda r: e5.three_way(emb, r, 0.8306, tl, judge, True), test, groups)
    lab = np.array([f"{groups[i]}|{l}" for i, l in zip(test, labels)])
    key = np.array([f"{groups[i]}|{t}" for i, t in zip(test, truth)])
    _, iss = np.unique(key, return_inverse=True)
    p, r, f = prf(*counts(lab, iss, np.ones(iss.max() + 1)))[:3]
    res[tl] = (p, r, banded / len(test))
    out.append(f"  t_low {tl}: P {p:.3f}  R {r:.3f}  F1 {f:.3f}  judged {banded / len(test):.0%}")
    print(out[-1], flush=True)
ok = (res[0.40][0] >= res[0.26][0] - 0.01 and res[0.40][1] >= res[0.26][1] - 0.03 and res[0.26][2] - res[0.40][2] >= 0.10)
out.append("RULE: " + ("ADOPT t_low = 0.40 for short-text channels" if ok else "keep t_low = 0.26 everywhere (0.40 not confirmed on unseen short reviews)"))
out.append("Caveat: labels are the agreed key of two LLM labellers (kappa 0.38), not human labels.")
print("\n".join(out[-2:]))
open(os.path.join(HERE, "results", "tlow_short_text_results.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
