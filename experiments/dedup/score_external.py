"""Score a colleague's pipeline (complaint_ref -> case_id CSVs) against R1 / R1+RJ1 on R1's held-out halves.
Optional: external/calibration_pair_ids.csv -> also score only pairs whose reviews are outside her 162 calibration IDs."""
import os, sys
import numpy as np, pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rejoin as rj
from ci_bootstrap import counts, prf

HERE = os.path.dirname(os.path.abspath(__file__))
EXT = {"CE pf": "eval_playstore_pf_thr048.csv", "CE global": "eval_playstore_global_thr048.csv"}
ext = {k: pd.read_csv(os.path.join(HERE, "external", f)).set_index("complaint_ref")["case_id"].astype(str) for k, f in EXT.items()}
cal_path = os.path.join(HERE, "external", "calibration_pair_ids.csv")
cal = None
if os.path.exists(cal_path):
    c = pd.read_csv(cal_path); cal = set(c.id_a) | set(c.id_b)

parts = []
for seed, h in ((0, "A"), (1, "B"), (1, "A")):
    r = rj.rebuild("playstore", seed, h)
    refs = r["refs"][r["test"]]
    sys_ = {"R1": np.array([f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], r["labels"])])}
    sys_["R1+RJ1"], _, _ = rj.run_variant(r, rj.PairJudge(r["texts"], r["refs"], "playstore"), 1)
    for k, s in ext.items():
        sys_[k] = s.reindex(refs).to_numpy()
    _, iss = np.unique(r["issues"][r["test"]], return_inverse=True)
    parts.append((iss, sys_, refs))

def pooled(keep_fn, w_list=None):
    out = {}
    for name in parts[0][1]:
        t = np.zeros(3)
        for j, (iss, s, refs) in enumerate(parts):
            m = keep_fn(refs)
            i2 = np.unique(iss[m], return_inverse=True)[1]
            w = np.ones(i2.max() + 1) if w_list is None else w_list[j][np.unique(iss[m])]
            t += counts(s[name][m].astype(str), i2, w)
        out[name] = t
    return out

def report(title, keep_fn):
    pt = pooled(keep_fn)
    rng = np.random.default_rng(0); boots = {k: [] for k in pt}
    for _ in range(1000):
        ws = [np.bincount(rng.integers(0, iss.max() + 1, iss.max() + 1), minlength=iss.max() + 1).astype(float) for iss, _, _ in parts]
        for k, t in pooled(keep_fn, ws).items():
            boots[k].append(prf(*t)[:3])
    n = sum(keep_fn(refs).sum() for _, _, refs in parts)
    lines = [f"{title} ({n} complaints over 3 held-out halves)"]
    for k, t in pt.items():
        p, rc, f = prf(*t)[:3]; lo, hi = np.percentile(np.array(boots[k]), [2.5, 97.5], axis=0)
        lines.append(f"  {k:10s} P {p:.3f} [{lo[0]:.2f},{hi[0]:.2f}]  R {rc:.3f} [{lo[1]:.2f},{hi[1]:.2f}]  F1 {f:.3f}")
    return lines

lines = ["EXTERNAL CE PIPELINE (threshold 0.4834, commit 8801740) vs R1, same held-out halves"]
lines += report("All held-out complaints (in-sample for CE: its threshold saw ~125 of these reviews)", lambda refs: np.ones(len(refs), bool))
if cal is not None:
    lines += report("Excluding CE's 162 calibration reviews (held-out for both)", lambda refs: ~np.isin(refs, list(cal)))
else:
    lines.append("(calibration_pair_ids.csv not provided yet: held-out-for-both view pending)")
txt = "\n".join(lines); print(txt)
open(os.path.join(HERE, "results", "external_ce_comparison.txt"), "w", encoding="utf-8").write(txt + "\n")
