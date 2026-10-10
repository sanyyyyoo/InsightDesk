"""
Agreement check on the team's Play Store labels (Overlap rows, all 3 people).

  Fleiss kappa on exact problem codes and on areas, with item bootstrap CI;
  pair-level agreement: do two people mark the same review pairs as duplicates
  (same product + same scored code)?

Input : labelling/team_labels_v3_table.csv (flattened from the team's sheet)
Output: labelling/overlap_disagreements.csv
"""

import argparse
import itertools
import os

import numpy as np
import pandas as pd

HERE = os.path.dirname(__file__)
UNSCORED = {"other", "not_a_problem", "not_about_this_app"}


def fleiss_kappa(ratings):
    """ratings: items x raters array of category labels."""
    cats = sorted(set(ratings.ravel()))
    n = ratings.shape[1]
    counts = np.array([[np.sum(r == c) for c in cats] for r in ratings])
    p_j = counts.sum(0) / counts.sum()
    p_i = ((counts ** 2).sum(1) - n) / (n * (n - 1))
    pe = (p_j ** 2).sum()
    return (p_i.mean() - pe) / (1 - pe)


def boot_ci(ratings, reps=2000, seed=0):
    rng = np.random.default_rng(seed)
    vals = []
    for _ in range(reps):
        s = ratings[rng.integers(0, len(ratings), len(ratings))]
        if len(set(s.ravel())) > 1:
            vals.append(fleiss_kappa(s))
    return np.percentile(vals, [2.5, 97.5])


def scored(code):
    return code not in UNSCORED and not code.endswith("unspecified")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", default="team_labels_v3_table.csv", help="file in labelling/")
    ap.add_argument("--out", default="overlap_disagreements.csv")
    args = ap.parse_args()
    t = pd.read_csv(os.path.join(HERE, "labelling", args.table), keep_default_na=False)
    ov = t[t.task == "Overlap"].pivot(index="row", columns="labeller", values="problem_code")
    full = ov[(ov != "").all(axis=1)]
    print(f"overlap rows labelled by all 3: {len(full)} of {len(ov)}")

    r = full.values.astype(str)
    k, (lo, hi) = fleiss_kappa(r), boot_ci(r)
    print(f"Fleiss kappa, exact code : {k:.3f}  95% CI [{lo:.3f}, {hi:.3f}]")
    area = pd.read_csv(os.path.join(HERE, "labels", "playstore_codebook.csv")).set_index("problem_code").area
    ra = full.apply(lambda col: col.map(lambda c: area.get(c, c))).values.astype(str)
    k2, (lo2, hi2) = fleiss_kappa(ra), boot_ci(ra)
    print(f"Fleiss kappa, area level : {k2:.3f}  95% CI [{lo2:.3f}, {hi2:.3f}]")
    nu = full.nunique(axis=1)
    print(f"all 3 agree {int((nu == 1).sum())} | 2 of 3 {int((nu == 2).sum())} | all differ {int((nu == 3).sum())}")
    for a, b in itertools.combinations(full.columns, 2):
        print(f"  {a} vs {b}: same code on {(full[a] == full[b]).mean():.0%}")

    prod = t[t.task == "Overlap"].drop_duplicates("row").set_index("row")["product"]

    def dup_pairs(col):
        return {(i, j) for i, j in itertools.combinations(full.index, 2)
                if prod[i] == prod[j] and full.at[i, col] == full.at[j, col] and scored(full.at[i, col])}

    P = {c: dup_pairs(c) for c in full.columns}
    print("duplicate pairs each person marks (same product + same scored code):",
          {c: len(p) for c, p in P.items()})
    for a, b in itertools.combinations(full.columns, 2):
        u = P[a] | P[b]
        print(f"  {a} vs {b}: shared {len(P[a] & P[b])} of {len(u)} (Jaccard {len(P[a] & P[b]) / len(u) if u else 1:.2f})")

    text = t[t.task == "Overlap"].drop_duplicates("row").set_index("row").review_text
    dis = full[nu > 1].assign(review=text.reindex(full[nu > 1].index))
    dis.to_csv(os.path.join(HERE, "labelling", args.out))
    pd.set_option("display.width", 250)
    print(dis.assign(review=dis.review.str.slice(0, 80)).to_string())


if __name__ == "__main__":
    main()
