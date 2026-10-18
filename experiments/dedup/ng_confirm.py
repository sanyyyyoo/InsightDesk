"""
"No hard gate" (NG) confirmation and NG + re-joining (rule: results/no_gate_confirm_rule.md).
Uses cached judge answers; the NG runs are made with e5_three_way.py --judge-prompt strict beforehand.
Re-joining on NG cases makes its own (cached) case-pair calls.

  python experiments/dedup/ng_confirm.py
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rejoin as rj  # noqa: E402
from ci_bootstrap import counts, prf  # noqa: E402

B, SEED = 2000, 11


def labels_for(data, seed, half, cal, prompt, with_rejoin):
    r = rj.rebuild(data, seed, half, calibrate=cal, prompt=prompt)
    base = np.array([f"{r['groups'][i]}|{l}" for i, l in zip(r["test"], r["labels"])])
    out = {"base": base, "issue": r["issues"][r["test"]], "misses": r["misses"]}
    if with_rejoin:
        pj = rj.PairJudge(r["texts"], r["refs"], data)
        lab, merges, _ = rj.run_variant(r, pj, 1)
        out["rejoin"] = lab.astype(str)
        out["merges"] = (len(merges), sum(x == y for x, y in merges))
    return out


def boot(parts, a, b):
    """Paired cluster bootstrap pooled over parts: point a, point b, CI of (b - a)."""
    rng = np.random.default_rng(SEED)
    prep = []
    for issue, preds in parts:
        _, iss = np.unique(np.asarray(issue).astype(str), return_inverse=True)
        prep.append((iss, iss.max() + 1, np.asarray(preds[a]).astype(str), np.asarray(preds[b]).astype(str)))
    pa = prf(*sum(np.array(counts(x, i, np.ones(n))) for i, n, x, _ in prep))
    pb = prf(*sum(np.array(counts(y, i, np.ones(n))) for i, n, _, y in prep))
    d = []
    for _ in range(B):
        ta, tb = np.zeros(3), np.zeros(3)
        for i, n, x, y in prep:
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            ta += counts(x, i, w)
            tb += counts(y, i, w)
        d.append(np.array(prf(*tb)) - np.array(prf(*ta)))
    lo, hi = np.percentile(np.array(d), [2.5, 97.5], axis=0)
    return pa, pb, lo, hi


def fmt(p):
    return f"P {p[0]:.3f} R {p[1]:.3f} F1 {p[2]:.3f}"


def main():
    lines = ["NO HARD GATE (NG) CONFIRMATION (rule: results/no_gate_confirm_rule.md)"]
    bug = {}
    for data in ("firefox3", "thunderbird"):
        g = labels_for(data, None, None, True, "gated", True)
        s = labels_for(data, None, None, True, "strict", True)
        assert (g["issue"] == s["issue"]).all()
        bug[data] = {"issue": g["issue"], "R1": g["base"], "R1+RJ1": g["rejoin"], "NG": s["base"], "NG+RJ1": s["rejoin"]}
        pr = {k: prf(*counts(v, np.unique(g["issue"], return_inverse=True)[1],
                             np.ones(len(set(g["issue"]))))) for k, v in bug[data].items() if k != "issue"}
        lines.append(f"\n{data} (cache misses R1 {g['misses']}, NG {s['misses']}; RJ1 merges on NG {s['merges'][0]}, "
                     f"{s['merges'][1]} correct)")
        for k, p in pr.items():
            lines.append(f"  {k:8s} {fmt(p)}")
        bug[data]["_p"] = pr
    parts = [(bug[d]["issue"], bug[d]) for d in bug]
    pa, pb, lo, hi = boot(parts, "R1", "NG")
    lines.append(f"\nFirefox 3 + Thunderbird pooled: R1 {fmt(pa)} | NG {fmt(pb)} | NG - R1: P {pb[0] - pa[0]:+.3f} "
                 f"[{lo[0]:+.3f},{hi[0]:+.3f}], R {pb[1] - pa[1]:+.3f} [{lo[1]:+.3f},{hi[1]:+.3f}]")
    ng_rec_ok = lo[1] > 0
    qa, qb, qlo, qhi = boot(parts, "NG", "NG+RJ1")
    lines.append(f"  NG+RJ1 {fmt(qb)} | NG+RJ1 - NG: P {qb[0] - qa[0]:+.3f} [{qlo[0]:+.3f},{qhi[0]:+.3f}], "
                 f"R {qb[1] - qa[1]:+.3f} [{qlo[1]:+.3f},{qhi[1]:+.3f}]")
    ra, rb, rlo, rhi = boot(parts, "R1+RJ1", "NG+RJ1")
    lines.append(f"  (for reference) NG+RJ1 - R1+RJ1: P {rb[0] - ra[0]:+.3f} [{rlo[0]:+.3f},{rhi[0]:+.3f}], "
                 f"R {rb[1] - ra[1]:+.3f} [{rlo[1]:+.3f},{rhi[1]:+.3f}]")

    # new apps (secondary): R1 vs NG against the agreed key
    import glob
    from new_apps_score import TAG, agreed, harness, key
    NA = os.path.abspath(os.path.join(HERE, "..", "..", "data", "external", "new_apps"))
    t = pd.read_csv(os.path.join(NA, "new_apps_test588.csv"))
    kx, _ = key(sorted(glob.glob(os.path.join(NA, "sheetX_*.xlsx")))[0])
    ky, _ = key(sorted(glob.glob(os.path.join(NA, "sheetY_*.xlsx")))[0])
    ka = agreed(kx, ky)
    ref = lambda r: r - 1_000_001
    r1 = harness("new_apps", "llm", f"llm_{TAG}_founder_gated_ext_playstore", ref)
    ng = harness("new_apps", "llm", f"llm_{TAG}_founder_strict_ext_playstore", ref)
    na_ok = None
    if r1 is not None and ng is not None and len(ng) == len(t):
        idx = t.index
        na_parts = [(ka.reindex(idx).astype(str).to_numpy(),
                     {"R1": r1.reindex(idx).astype(str).to_numpy(), "NG": ng.reindex(idx).astype(str).to_numpy()})]
        a1, b1, l1, h1 = boot(na_parts, "R1", "NG")
        na_ok = (b1[0] - a1[0]) >= -0.05
        lines.append(f"\nnew apps 588 (agreed key): R1 {fmt(a1)} | NG {fmt(b1)} | NG - R1: P {b1[0] - a1[0]:+.3f} "
                     f"[{l1[0]:+.3f},{h1[0]:+.3f}], R {b1[1] - a1[1]:+.3f} [{l1[1]:+.3f},{h1[1]:+.3f}]")
    else:
        lines.append("\nnew apps: NG run not available")
    ff, tb = bug["firefox3"]["_p"]["NG"], bug["thunderbird"]["_p"]["NG"]
    tb_r1 = bug["thunderbird"]["_p"]["R1"]
    ng_ok = ff[0] >= 0.90 and tb[0] >= tb_r1[0] - 0.03 and ng_rec_ok and bool(na_ok)
    lines.append(f"\nRULE 1 (NG): {'ADOPT' if ng_ok else 'not adopted'} - Firefox 3 P {ff[0]:.3f} >= 0.90? "
                 f"Thunderbird P {tb[0]:.3f} >= {tb_r1[0] - 0.03:.3f}? pooled recall CI low {lo[1]:+.3f} > 0? "
                 f"new apps precision drop within 0.05? {na_ok}")
    combo_ok = ng_ok and qb[0] >= 0.88 and qlo[1] > 0
    lines.append(f"RULE 2 (NG+RJ1 over NG): {'ADOPT' if combo_ok else 'not adopted'} - pooled P {qb[0]:.3f} >= 0.88? "
                 f"recall CI low {qlo[1]:+.3f} > 0?")
    text = "\n".join(lines)
    print(text)
    open(os.path.join(HERE, "results", "no_gate_confirm_results.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
