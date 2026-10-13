"""
Coverage check for the cluster-bootstrap intervals (old counts_v1 vs corrected counts).
Simulated test sets shaped like the Play Store set (~340 reviews, ~half singletons, groups of
2-20) with a dedup that splits groups (low recall) and wrongly merges parts of different groups.
True value = pooled precision / recall over 4000 independent test sets from the same process.
Coverage = share of 300 simulated test sets whose 95% interval (1000 resamples) contains it.

  python experiments/dedup/ci_coverage_sim.py
"""
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
from ci_bootstrap import c2, counts  # noqa: E402

rng = np.random.default_rng(7)


def counts_v1_fast(case, issue, w):
    _, cidx = np.unique(case, return_inverse=True)
    cells, n = np.unique(np.stack([cidx, issue]), axis=1, return_counts=True)
    cc, wi = cells[0], w[cells[1]]
    N, S = n * wi, n * c2(wi)
    tp = (c2(N) - S).sum()
    pred = (c2(np.bincount(cc, weights=N)) - np.bincount(cc, weights=S)).sum()
    ni = np.bincount(issue, minlength=len(w))
    true = (c2(ni * w) - ni * c2(w)).sum()
    return tp, pred, true


def dataset(merge_p):
    sizes = np.where(rng.random(150) < 0.5, 1, np.minimum(2 + rng.geometric(0.22, 150), 20))
    issue = np.repeat(np.arange(len(sizes)), sizes)
    part = np.zeros(len(issue), int)
    nxt = 0
    for g in range(len(sizes)):                 # split each group into 1-3 cases (missed duplicates)
        idx = np.where(issue == g)[0]
        k = min(len(idx), rng.integers(1, 4))
        part[idx] = nxt + rng.integers(0, k, len(idx))
        nxt += k
    case = part.copy()
    for c in np.unique(part):                   # wrongly merge some parts into another group's case
        if rng.random() < merge_p:
            case[part == c] = rng.choice(part)
    return case, issue


def prf(t):
    tp, pred, true = t
    return np.array([tp / pred if pred else 0, tp / true if true else 0])


for merge_p in (0.10, 0.30, 0.60):
    tot = np.zeros(3)
    for _ in range(4000):
        c, i = dataset(merge_p)
        tot += np.array(counts(c, i, np.ones(i.max() + 1)))
    truth = prf(tot)
    cover = {"old (v1)": np.zeros(2), "corrected": np.zeros(2)}
    R = 300
    for _ in range(R):
        c, i = dataset(merge_p)
        n = i.max() + 1
        bs = {"old (v1)": [], "corrected": []}
        for _ in range(1000):
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            bs["old (v1)"].append(prf(counts_v1_fast(c, i, w)))
            bs["corrected"].append(prf(counts(c, i, w)))
        for k, v in bs.items():
            lo, hi = np.percentile(np.array(v), [2.5, 97.5], axis=0)
            cover[k] += (lo <= truth) & (truth <= hi)
    print(f"merge errors {merge_p:.0%}: true precision {truth[0]:.3f}, recall {truth[1]:.3f} | 95% interval coverage "
          + " | ".join(f"{k}: P {v[0] / R:.0%} R {v[1] / R:.0%}" for k, v in cover.items()), flush=True)
