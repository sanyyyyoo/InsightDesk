"""
Score R1 on Mozilla as one company with and without the product filter
(rule: results/one_company_no_product_rule.md). No LLM calls.

  python experiments/dedup/one_company_score.py
"""

import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import e5_three_way as e5  # noqa: E402
from ci_bootstrap import bcubed, counts, prf  # noqa: E402
from spike_grouping import G, load  # noqa: E402

B, SEED = 2000, 11


def main():
    m = pd.read_csv(os.path.join(ROOT, "data", "external", "mozilla_combined.csv"))
    off = e5.EXT_REF_OFFSET
    nofilter = load(f"mozilla_combined_e5_assignments_single_oracle_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "mozilla_combined")
    single = load(f"mozilla_combined_e5_assignments_single_oracle_llm_{G}_founder_gated_ext_playstore", "single", "ext", "mozilla_combined")
    oracle = load(f"mozilla_combined_e5_assignments_single_oracle_llm_{G}_founder_gated_ext_playstore", "oracle", "ext", "mozilla_combined")
    ff = load(f"firefox3_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox3")
    tb = load(f"thunderbird_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "thunderbird")
    filt = {}
    for r in m.itertuples():
        src = ff if r.product == "Firefox" else tb
        filt[r.complaint_ref + off] = f"{r.product}|{src[r.orig_ref + off]}"
    refs = [r + off for r in m.complaint_ref]
    issue = m.issue_id.astype(str).to_numpy()
    prod = m["product"].to_numpy()
    runs = {"R1, product filter (known product)": np.array([filt[r] for r in refs]),
            "R1, NO product filter (one stream)": nofilter.reindex(refs).astype(str).to_numpy(),
            "cosine only, no filter": single.reindex(refs).astype(str).to_numpy(),
            "oracle, no filter (ceiling)": oracle.reindex(refs).astype(str).to_numpy()}
    _, iss = np.unique(issue, return_inverse=True)
    n = iss.max() + 1
    lines = [f"Mozilla as one company: {len(m)} reports (Firefox 437, Thunderbird 452); "
             f"{int((pd.Series(issue).value_counts() >= 2).sum())} duplicate groups"]
    pts, boot = {}, {k: [] for k in runs}
    rng = np.random.default_rng(SEED)
    for k, v in runs.items():
        pts[k] = prf(*counts(v, iss, np.ones(n)))
    for _ in range(B):
        w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
        for k, v in runs.items():
            boot[k].append(prf(*counts(v, iss, w)))
    for k, v in runs.items():
        lo, hi = np.percentile(np.array(boot[k]), [2.5, 97.5], axis=0)
        bp, br, _ = bcubed(v, iss, np.ones(n))
        cases = pd.Series(prod).groupby(v).agg(lambda s: s.nunique())
        sizes = pd.Series(v).value_counts()
        multi = sizes[sizes >= 2].index
        mixed = [c for c in multi if cases[c] > 1]
        lines.append(f"  {k:36s} P {pts[k][0]:.3f} [{lo[0]:.2f},{hi[0]:.2f}]  R {pts[k][1]:.3f} [{lo[1]:.2f},{hi[1]:.2f}]  "
                     f"F1 {pts[k][2]:.3f}  case P {bp:.3f} | multi-report cases {len(multi)}, mixing products "
                     f"{len(mixed)} ({len(mixed) / max(1, len(multi)):.1%}), complaints in them {int(sizes[mixed].sum())}")
    a, b = "R1, NO product filter (one stream)", "R1, product filter (known product)"
    d = np.array(boot[a]) - np.array(boot[b])
    lo, hi = np.percentile(d, [2.5, 97.5], axis=0)
    lines.append(f"  no filter minus filter: P {pts[a][0] - pts[b][0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}], "
                 f"R {pts[a][1] - pts[b][1]:+.3f} [{lo[1]:+.3f},{hi[1]:+.3f}], F1 {pts[a][2] - pts[b][2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
    v = runs[a]
    sizes = pd.Series(v).value_counts()
    mixed = [c for c in sizes[sizes >= 2].index if pd.Series(prod[v == c]).nunique() > 1]
    big_drop = (pts[b][0] - pts[a][0]) > 0.05 or len(mixed) / max(1, (sizes >= 2).sum()) > 0.05
    lines.append("READING (pre-declared): " + ("a product or area field should be captured when a company has several products"
                                               if big_drop else "R1 is usable without a product field"))
    print("\n".join(lines))


if __name__ == "__main__":
    main()
