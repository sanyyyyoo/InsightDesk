"""
E8: per-product dedup and leave-one-product-out (LOPO) calibration on the
team-labelled Play Store reviews.

Deployment framing: dedup runs WITHIN one company's complaint stream;
"generic" = the method and its threshold are calibrated WITHOUT the target
company's data.

  per product : each product's reviews are clustered on their own (in date
                order for the online pipeline); pairs are only formed within
                a product; TP/FP/FN are summed over products (micro).
  LOPO        : threshold tuned on the other 5 products (best pooled F1 with
                precision >= 0.90, the rule used throughout), applied to the
                held-out product. Compared with the threshold tuned on the
                product itself (in-product upper bound) -> transfer gap.

Variants: v2 cleaned text + MiniLM; SimCSE + synonyms; LLM issue statement
(comparison only, cached rewrites - no new API calls).

  python experiments/dedup/e8_per_product.py
"""

import os
import sys
from itertools import combinations

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from compare_pipelines import batch_cos, online_cos  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, llm_cache_path  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
GRID = np.round(np.arange(0.30, 0.96, 0.02), 3)
MIN_P = 0.90


def counts(labels, issues):
    tp = fp = fn = 0
    for a, b in combinations(range(len(labels)), 2):
        sc, si = labels[a] == labels[b], issues[a] == issues[b]
        tp += sc and si
        fp += sc and not si
        fn += si and not sc
    return np.array([tp, fp, fn])


def prf(c):
    tp, fp, fn = c
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def table(emb, df, products, run):
    """counts[product][threshold index] for one pipeline."""
    out = {}
    for prod in products:
        rows = np.where(df.department.values == prod)[0]
        iss = df.issue_id.values[rows]
        out[prod] = np.array([counts(run(emb[rows], t), iss) for t in GRID])
    return out


def pick(c):
    """Index of best F1 with precision >= MIN_P (fallback: highest threshold)."""
    best, best_f1 = len(GRID) - 1, -1.0
    for i, ci in enumerate(c):
        p, _, f = prf(ci)
        if p >= MIN_P and f > best_f1:
            best, best_f1 = i, f
    return best


def main():
    from sentence_transformers import SentenceTransformer
    base = load_ground_truth(path=DATA_PATHS["playstore"])
    base["issue_id"] = base.issue_id.astype(str)
    base["department"] = base.department.astype(str)
    minilm = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    simcse = SentenceTransformer(os.path.join(os.path.dirname(__file__), "models", "minilm-simcse"))

    syn = apply_text_mode(base, "boilerplate+synonyms", minilm, data="playstore")
    llm = apply_text_mode(base, "llm", minilm, data="playstore")
    assert pd.read_csv(llm_cache_path("playstore")).complaint_ref.nunique() == len(base)
    variants = {
        "v2 MiniLM (cleaned)": minilm.encode(base.cleaned_text.tolist(), normalize_embeddings=True),
        "SimCSE + synonyms": simcse.encode(syn.cleaned_text.tolist(), normalize_embeddings=True),
        "LLM issue statement (comparison)": minilm.encode(llm.cleaned_text.tolist(), normalize_embeddings=True),
    }
    products = sorted(base.department.unique())
    size = base.department.value_counts()
    dup_pairs = {p: int(counts(np.arange(n := (base.department == p).sum()), base.issue_id[base.department == p].values)[2])
                 for p in products}
    print("reviews / duplicate pairs per product:", {p: (int(size[p]), dup_pairs[p]) for p in products})

    rows = []
    for vname, emb in variants.items():
        for pname, run in (("online", lambda e, t: online_cos(e, t)), ("batch", lambda e, t: batch_cos(e, t))):
            c = table(emb, base, products, run)
            pooled = sum(c.values())
            # ceiling: one threshold for all products, chosen on all of them (not held out)
            i_all = pick(pooled)
            for held in products:
                rest = sum(c[p] for p in products if p != held)
                i_lopo, i_self = pick(rest), pick(c[held])
                for kind, i in (("lopo", i_lopo), ("self", i_self), ("pooled", i_all)):
                    p, r, f = prf(c[held][i])
                    rows.append({"variant": vname, "pipeline": pname, "held_out": held, "kind": kind,
                                 "threshold": GRID[i], "tp": c[held][i][0], "fp": c[held][i][1], "fn": c[held][i][2],
                                 "P": p, "R": r, "F1": f, "reviews": int(size[held]), "dup_pairs": dup_pairs[held]})
            print(f"done {vname} / {pname}", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "e8_per_product.csv"), index=False)
    # micro-average over products: sum tp/fp/fn
    agg = out.groupby(["variant", "pipeline", "kind"])[["tp", "fp", "fn"]].sum()
    agg[["P", "R", "F1"]] = [prf(r) for r in agg[["tp", "fp", "fn"]].values]
    pd.set_option("display.width", 220)
    print("\nMICRO over the 6 products (sum of held-out products):")
    print(agg.round(3).to_string())
    lo = out[out.kind == "lopo"].pivot_table(index="held_out", columns=["variant", "pipeline"], values="F1")
    print("\nLOPO F1 per held-out product:")
    print(lo.round(3).to_string())
    print("\nLOPO thresholds chosen:")
    print(out[out.kind == "lopo"].pivot_table(index="held_out", columns=["variant", "pipeline"], values="threshold").to_string())


if __name__ == "__main__":
    main()
