"""
Leave-one-product-out: is the dedup threshold generic across companies?

For each product P (a stand-in for one company):
  tune  = reviews of the OTHER products (clustered per product)
          threshold = best pairwise F1 with precision >= 0.90 (same rule as
          compare_pipelines.pick_threshold)
  test  = reviews of P only, clustered with that threshold
Reported per product and pooled over all test pairs (micro), so tiny
products do not dominate the average.

  python experiments/dedup/leave_one_product_out.py --data playstore
"""

import argparse
import os
import re
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))

from compare_pipelines import batch_cos, evaluate, online_cos, per_product, pick_threshold  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from backend.services.preprocess import clean_text  # noqa: E402

# Product, vendor and competitor names seen in the reviews. Stripped from the
# TEXT only (--strip-brands); the per-product filter is unchanged.
BRANDS = re.compile(
    r"\b(zen\s*desk|fresh\s*desk|fresh\s*works?|freshservice|zoho(\s*desk)?|help\s*scout|live\s*agent|"
    r"happy\s*fox|intuit|tawk\.?to|corrigo|support\s*desk)\b", re.I)


def strip_brands(text):
    return re.sub(r"\s{2,}", " ", BRANDS.sub(" ", text)).strip()

OUT_DIR = os.path.join(os.path.dirname(__file__), "results")
GRID = np.round(np.arange(0.30, 0.96, 0.02), 3)
SETUPS = [  # (name, encoder, text mode)
    ("MiniLM raw", "sentence-transformers/all-MiniLM-L6-v2", "raw"),
    ("SimCSE + synonyms", os.path.join(os.path.dirname(__file__), "models", "minilm-simcse"), "boilerplate+synonyms"),
]


def pair_counts(labels, issues):
    """TP / FP / FN pair counts (for pooling across products)."""
    iu = np.triu_indices(len(labels), 1)
    sc = (labels[:, None] == labels[None, :])[iu]
    si = (issues[:, None] == issues[None, :])[iu]
    return int((sc & si).sum()), int((sc & ~si).sum()), int((~sc & si).sum())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="playstore", choices=list(DATA_PATHS))
    parser.add_argument("--strip-brands", action="store_true",
                        help="remove product/vendor names from the text before embedding")
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer
    minilm = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    base = load_ground_truth(path=DATA_PATHS[args.data])
    products = np.array(base["department"].astype(str).tolist())   # plain numpy (not Arrow-backed)
    issues = np.array(base["issue_id"].astype(str).tolist())
    if args.strip_brands:
        before = base["complaint_text"].astype(str)
        base = base.assign(complaint_text=before.map(strip_brands))
        base["cleaned_text"] = base["complaint_text"].map(clean_text)
        changed = int((before != base["complaint_text"]).sum())
        left = int(base["complaint_text"].str.contains(BRANDS).sum())
        print(f"brand names stripped from {changed} reviews; remaining matches: {left}")

    rows = []
    for setup, model, mode in SETUPS:
        df = base if mode == "raw" else apply_text_mode(base, mode, minilm, data=args.data)
        enc = minilm if model.endswith("MiniLM-L6-v2") else SentenceTransformer(model)
        emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
        for pipe, run in (("online-cos", lambda d, e, t: online_cos(e, t)),
                          ("batch-cos", lambda d, e, t: batch_cos(e, t))):
            run_pp = per_product(run)
            for p in pd.unique(products):
                tune = np.where(products != p)[0]
                test = np.where(products == p)[0]
                t = pick_threshold(run_pp, df, emb, tune, GRID)
                labels = np.asarray(run(df.iloc[test].reset_index(drop=True), emb[test], t))
                m = evaluate(labels, issues[test], np.arange(len(test)))
                tp, fp, fn = pair_counts(labels, issues[test])
                g = pd.Series(issues[test]).value_counts()
                m.update({"setup": setup, "pipeline": pipe, "held_out_product": p, "threshold": t,
                          "reviews": len(test), "true_dup_pairs": int((g * (g - 1) // 2).sum()),
                          "tp": tp, "fp": fp, "fn": fn})
                rows.append(m)
                print(f"{setup:18s} {pipe:10s} test={p:11s} n={len(test):3d} t={t:.2f} "
                      f"P={m['pair_precision']:.3f} R={m['pair_recall']:.3f} F1={m['pair_f1']:.3f} "
                      f"tp={tp} fp={fp} fn={fn}", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(OUT_DIR, f"lopo_{args.data}{'_nobrand' if args.strip_brands else ''}.csv"), index=False)
    pooled = out.groupby(["setup", "pipeline"])[["tp", "fp", "fn"]].sum()
    pooled["precision"] = pooled.tp / (pooled.tp + pooled.fp).clip(lower=1)
    pooled["recall"] = pooled.tp / (pooled.tp + pooled.fn).clip(lower=1)
    pooled["f1"] = 2 * pooled.precision * pooled.recall / (pooled.precision + pooled.recall).replace(0, np.nan)
    pooled["threshold_range"] = out.groupby(["setup", "pipeline"]).threshold.agg(lambda s: f"{s.min():.2f}-{s.max():.2f}")
    print("\npooled over held-out products (micro):\n", pooled.round(3).to_string())


if __name__ == "__main__":
    main()
