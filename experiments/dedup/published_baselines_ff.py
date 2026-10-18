"""Firefox 3 transfer: each method's threshold tuned on ALL Play Store reviews (best F1), applied unchanged
to Firefox 3, as InsightDesk's thresholds are (addendum in published_baselines_rule.md)."""
import os, re, math, hashlib
from collections import Counter
import numpy as np
import published_baselines as pb
from ci_bootstrap import counts, prf
from normalize import DATA_PATHS
from replay_lab import load_ground_truth

all_ps = np.arange(len(pb.TXT))
chosen = {n: max(g, key=lambda t: prf(*pb.score(all_ps, pb.online(all_ps, s, t)))[2]) for n, (s, g) in pb.METHODS.items()}
ff = load_ground_truth(path=DATA_PATHS["firefox3"])
pb.TXT = ff["complaint_text"].astype(str).tolist(); pb.ISS = np.array(ff["issue_id"].astype(str).tolist())
pb.GRP = np.array(ff["department"].astype(str).tolist()); N = len(pb.TXT)
pb.TOK = [[w for w in re.findall(r"[a-z][a-z0-9']+", t.lower()) if w not in pb.SW] for t in pb.TXT]
DF = Counter(w for t in pb.TOK for w in set(t)); pb.AVG = np.mean([max(len(t), 1) for t in pb.TOK])
pb.IDF = {w: math.log(1 + (N - n + 0.5) / (n + 0.5)) for w, n in DF.items()}
pb.SELF = [pb.bm25(i, i) or 1.0 for i in range(N)]
pb.SH = [pb.shingles(t) for t in pb.TXT]; pb.SIM = [pb.simhash(t) for t in pb.TOK]
idx = np.arange(N)
out = [f"FIREFOX 3 ({N} reports), thresholds from Play Store"]
for n, (s, g) in pb.METHODS.items():
    p, r, f = prf(*pb.score(idx, pb.online(idx, s, chosen[n])))[:3]
    out.append(f"  {n:42s} P {p:.3f} R {r:.3f} F1 {f:.3f}  threshold {float(chosen[n])}"); print(out[-1], flush=True)
open(os.path.join(pb.HERE, "results", "published_baselines_firefox3.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
