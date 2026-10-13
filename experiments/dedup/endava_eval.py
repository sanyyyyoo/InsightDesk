"""
Endava help-desk tickets (rule: D:/PBL/InsightDesk-claude-review/reports/endava/endava_rule.md).

R1 (app replay) vs the main-branch pipeline on the same 1,000 tickets, scored at
the category level (category-sub1-sub2 code). Pairwise and case-level, with
cluster-bootstrap intervals and the paired difference.

  python experiments/dedup/endava_eval.py            # needs the R1 replay to have finished
  python experiments/dedup/endava_eval.py --main-only # just compute the main-branch replay
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.services.preprocess import clean_text  # noqa: E402

SAMPLE = "data/external/endava/endava_sample1000.csv"
R1 = "D:/PBL/InsightDesk-claude-review/reports/endava/replay_assignments.csv"
SAVED = "data/external/endava/main_branch_assignments.csv"
B, SEED = 2000, 11


def c2(x):
    return x * (x - 1) / 2.0


def main_branch(s):
    if os.path.exists(SAVED):
        return pd.read_csv(SAVED).production.to_numpy()
    from replay_lab import Models, Replay
    from sentence_transformers import CrossEncoder
    d = s.copy()
    d["issue_id"] = d.label
    d["cleaned_text"] = d.complaint_text.astype(str).map(clean_text)
    models = Models()
    models.cross_encoder, models._ce_cache = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2"), {}
    rep = Replay(d, models.embed(d["cleaned_text"]), models, "first", 5, -2.21).run()
    prod = pd.Series(rep.case_of_row).sort_index().to_numpy()
    pd.DataFrame({"row": range(len(prod)), "production": prod}).to_csv(SAVED, index=False)
    return prod


def scores(case, lab, w):
    """Pair and B-cubed P/R/F1 with the corrected cluster-bootstrap weighting (ci_bootstrap.py)."""
    from ci_bootstrap import bcubed, counts
    tp, pred, true = counts(case, lab, w)
    p, r = (tp / pred if pred else 0.0), (tp / true if true else 0.0)
    bp, br, bf = bcubed(case, lab, w)
    return np.array([p, r, 2 * p * r / (p + r) if p + r else 0, bp, br, bf])


def report(title, methods, labels):
    codes, lab = np.unique(labels, return_inverse=True)
    ones = np.ones(len(codes))
    pts = {k: scores(v, lab, ones) for k, v in methods.items()}
    rng = np.random.default_rng(SEED)
    boot = {k: [] for k in methods}
    for _ in range(B):
        w = np.bincount(rng.integers(0, len(codes), len(codes)), minlength=len(codes)).astype(float)
        for k, v in methods.items():
            boot[k].append(scores(v, lab, w))
    print(f"\n{title}  ({len(labels)} tickets, {len(codes)} category codes)")
    names = ["pair P", "pair R", "pair F1", "case P", "case R", "case F1"]
    for k in methods:
        lo, hi = np.percentile(np.array(boot[k]), [2.5, 97.5], axis=0)
        print(f"  {k:30s} " + " | ".join(f"{n} {pts[k][j]:.3f} [{lo[j]:.3f},{hi[j]:.3f}]" for j, n in enumerate(names)))
    ks = list(methods)
    if len(ks) == 2:
        d = np.array(boot[ks[1]]) - np.array(boot[ks[0]])
        for j, n in ((0, "pair P"), (2, "pair F1"), (3, "case P"), (5, "case F1")):
            lo, hi = np.percentile(d[:, j], [2.5, 97.5])
            print(f"  {ks[1]} - {ks[0]}: {n} {pts[ks[1]][j] - pts[ks[0]][j]:+.3f} [{lo:+.3f},{hi:+.3f}], "
                  f"ahead in {(d[:, j] > 0).mean():.0%} of resamples")


def main():
    s = pd.read_csv(SAMPLE)
    prod = main_branch(s)
    if "--main-only" in sys.argv:
        print("main-branch cases:", len(set(prod)))
        return
    r1s = pd.read_csv(R1).set_index("row").case_id
    if "--partial" in sys.argv:          # preliminary: the first N tickets both pipelines have processed
        n = int(r1s.index.max()) + 1
        print(f"PRELIMINARY: first {n} of {len(s)} tickets (both pipelines are online, so this prefix is like for like)")
        s, prod = s.iloc[:n].reset_index(drop=True), prod[:n]
    r1 = r1s.reindex(range(len(s))).to_numpy()
    methods = {"main branch (MS-MARCO -2.21)": prod, "R1 (app, real judge)": r1}
    for k, v in methods.items():
        size = pd.Series(v).value_counts()
        print(f"{k}: cases {len(size)}, multi-ticket {(size > 1).sum()}, largest {size.max()}")
    report("ALL TICKETS", methods, s.label.to_numpy())
    big = s.label.value_counts().index[0]
    keep = (s.label != big).to_numpy()
    report(f"EXCLUDING the largest category ({big})", {k: v[keep] for k, v in methods.items()}, s.label.to_numpy()[keep])


if __name__ == "__main__":
    main()
