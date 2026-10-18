"""
E10: SemHash (github.com/MinishLab/semhash) as an off-the-shelf baseline on
the team-labelled Play Store reviews.

SemHash = Model2Vec static embeddings (default minishlab/potion-base-8M) +
ANN search; self_deduplicate(threshold) drops a record when a kept record is
at least `threshold` similar (default 0.9). It is built for removing near-
duplicates from training data, i.e. threshold-based auto-merge.

  A. auto-merge: per product, record -> duplicate_of links become cases;
     pairwise P/R/F1 micro over products; threshold default 0.9 and
     leave-one-product-out (best F1 with precision >= 0.90, as in E8)
  B. suggestions: potion-base-8M embeddings in the E9 protocol (bucket RR@k)

  python experiments/dedup/e10_semhash.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from e8_per_product import counts, prf  # noqa: E402
from e9_dbrd_baselines import KS, rank_of_bucket, rr, test_items  # noqa: E402
from normalize import DATA_PATHS  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
GRID = np.round(np.arange(0.50, 0.99, 0.02), 3)


def semhash_cases(texts, threshold, model):
    from semhash import SemHash
    recs = [{"i": str(k), "text": t} for k, t in enumerate(texts)]
    res = SemHash.from_records(recs, columns=["text"], model=model).self_deduplicate(threshold=threshold)
    parent = list(range(len(texts)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for d in res.filtered:
        a = int(d.record["i"])
        for other in (d.duplicates if hasattr(d, "duplicates") else [(d.duplicate_of, d.score)]):
            o = other[0] if isinstance(other, tuple) else other
            if o is None:
                continue
            parent[find(a)] = find(int(o["i"]))
    return np.array([find(k) for k in range(len(texts))])


def main():
    from model2vec import StaticModel
    model = StaticModel.from_pretrained("minishlab/potion-base-8M")
    df = load_ground_truth(path=DATA_PATHS["playstore"])
    df["issue_id"] = df.issue_id.astype(str)
    df["department"] = df.department.astype(str)
    raw = df.complaint_text.astype(str).tolist()
    products = sorted(df.department.unique())

    # A. auto-merge
    c = {}
    for p in products:
        rows = np.where(df.department.values == p)[0]
        c[p] = np.array([counts(semhash_cases([raw[r] for r in rows], t, model), df.issue_id.values[rows]) for t in GRID])

    def pick(cc):
        best, bf = len(GRID) - 1, -1.0
        for i, ci in enumerate(cc):
            pp, _, f = prf(ci)
            if pp >= 0.90 and f > bf:
                best, bf = i, f
        return best

    i09 = int(np.where(np.isclose(GRID, 0.90))[0][0])
    default = sum(c[p][i09] for p in products)
    lopo = sum(c[p][pick(sum(c[q] for q in products if q != p))] for p in products)
    pooled = sum(c.values())
    best_any = max(range(len(GRID)), key=lambda i: prf(pooled[i])[2])
    print("A. SemHash auto-merge (micro over products):")
    for name, cc in (("default threshold 0.90", default), ("LOPO threshold", lopo),
                     (f"best F1 at any threshold ({GRID[best_any]}, not held out)", pooled[best_any])):
        pp, r, f = prf(cc)
        print(f"   {name:48s} TP={cc[0]:3d} FP={cc[1]:3d} FN={cc[2]:3d}  P={pp:.3f} R={r:.3f} F1={f:.3f}")

    # B. suggestions with potion-base-8M embeddings
    e = model.encode(raw)
    e = e / np.linalg.norm(e, axis=1, keepdims=True)
    items = test_items(df)
    iss = df.issue_id.values
    ranks = np.array([rank_of_bucket(e[prev] @ e[i], prev, iss, iss[i]) for i, prev in items])
    print("B. SemHash/Model2Vec as a suggester:", "  ".join(f"RR@{k}={rr(ranks, k):.3f}" for k in KS))
    pd.DataFrame({"rank": ranks}).to_csv(os.path.join(RESULTS, "e10_semhash_ranks.csv"), index=False)


if __name__ == "__main__":
    main()
