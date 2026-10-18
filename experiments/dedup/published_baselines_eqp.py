"""Equal-precision variant of published_baselines.py (addendum in published_baselines_rule.md)."""
import os
import numpy as np
import published_baselines as pb
from ci_bootstrap import prf

FLOOR = 0.80
ids = np.array(sorted(set(pb.ISS)))
out = [f"EQUAL PRECISION (tuning precision >= {FLOOR}) on Play Store held-out halves"]
for name, (sim, grid) in pb.METHODS.items():
    tot, chosen = np.zeros(3), []
    for seed, half in ((0, "A"), (1, "B"), (1, "A")):
        rng = np.random.default_rng(seed)
        h = set(rng.choice(ids, size=len(ids) // 2, replace=False))
        a, b = np.where(np.isin(pb.ISS, list(h)))[0], np.where(~np.isin(pb.ISS, list(h)))[0]
        tune, test = (a, b) if half == "B" else (b, a)
        res = {t: prf(*pb.score(tune, pb.online(tune, sim, t)))[:2] for t in grid}
        ok = [t for t, (p, r) in res.items() if p >= FLOOR and r > 0]
        th = max(ok, key=lambda t: res[t][1]) if ok else max(res, key=lambda t: res[t][0])
        chosen.append((float(th), bool(ok)))
        tot += pb.score(test, pb.online(test, sim, th))
    p, r, f = prf(*tot)[:3]
    out.append(f"  {name:42s} P {p:.3f}  R {r:.3f}  F1 {f:.3f}   threshold, reached floor on tuning: {chosen}")
    print(out[-1], flush=True)
out.append("  InsightDesk (with re-joining): P 0.799 R 0.327 | without: P 0.810 R 0.259")
open(os.path.join(pb.HERE, "results", "published_baselines_eqp.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
