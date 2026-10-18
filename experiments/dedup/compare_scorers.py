"""
E1: which similarity scorer separates duplicate from non-duplicate
complaint pairs best?

Pairs: data/calibration_pairs.csv (150; 75 duplicate, 50 hard negative,
25 easy negative). Scored on cleaned text, as in production, with and
without the generator's stock phrases.

  python experiments/dedup/compare_scorers.py
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from replay_lab import strip_generator_templates  # noqa: E402

PAIRS_PATH = "data/calibration_pairs.csv"
OUT = os.path.join(os.path.dirname(__file__), "results", "scorers.csv")

BI_ENCODERS = {
    "MiniLM-L6 (v1 retrieval)": ("sentence-transformers/all-MiniLM-L6-v2", ""),
    "MPNet-base": ("sentence-transformers/all-mpnet-base-v2", ""),
    "BGE-small-v1.5": ("BAAI/bge-small-en-v1.5", ""),
    "BGE-base-v1.5": ("BAAI/bge-base-en-v1.5", ""),
    "GTE-base": ("thenlper/gte-base", ""),
    "E5-base-v2": ("intfloat/e5-base-v2", "query: "),
}
CROSS_ENCODERS = {
    "STS-B CE (v1 rerank)": "cross-encoder/stsb-distilroberta-base",
    "Quora CE": "cross-encoder/quora-distilroberta-base",
}


def recall_at_precision(y, scores, target):
    best = 0.0
    for t in np.unique(scores):
        pred = scores >= t
        tp = int((pred & (y == 1)).sum())
        fp = int((pred & (y == 0)).sum())
        if tp + fp and tp / (tp + fp) >= target:
            best = max(best, tp / y.sum())
    return best


def evaluate(name, variant, y, scores):
    return {
        "scorer": name,
        "data": variant,
        "roc_auc": roc_auc_score(y, scores),
        "pr_auc": average_precision_score(y, scores),
        "recall@P>=0.90": recall_at_precision(y, scores, 0.90),
        "recall@P>=0.95": recall_at_precision(y, scores, 0.95),
    }


def main():
    from sentence_transformers import CrossEncoder, SentenceTransformer

    pairs = pd.read_csv(PAIRS_PATH)
    y = (pairs["true_label"] == "duplicate").astype(int).values

    variants = {
        "v1 data": (pairs.text_a, pairs.text_b),
        "stock phrases removed": (
            pairs.text_a.map(strip_generator_templates),
            pairs.text_b.map(strip_generator_templates),
        ),
    }

    rows, fusion_inputs = [], {}

    for variant, (a_raw, b_raw) in variants.items():
        a = a_raw.astype(str).map(clean_text).tolist()
        b = b_raw.astype(str).map(clean_text).tolist()
        fusion_inputs[variant] = {}

        for name, (model_id, prefix) in BI_ENCODERS.items():
            model = SentenceTransformer(model_id)
            ea = model.encode([prefix + t for t in a], normalize_embeddings=True, show_progress_bar=False)
            eb = model.encode([prefix + t for t in b], normalize_embeddings=True, show_progress_bar=False)
            scores = (ea * eb).sum(axis=1)
            fusion_inputs[variant][name] = scores
            rows.append(evaluate(name, variant, y, scores))
            print(f"{variant:22s} {name:26s} AUC={rows[-1]['roc_auc']:.3f} R@P90={rows[-1]['recall@P>=0.90']:.2f}", flush=True)

        for name, model_id in CROSS_ENCODERS.items():
            model = CrossEncoder(model_id)
            scores = np.asarray(model.predict(list(zip(a, b)), show_progress_bar=False))
            fusion_inputs[variant][name] = scores
            rows.append(evaluate(name, variant, y, scores))
            print(f"{variant:22s} {name:26s} AUC={rows[-1]['roc_auc']:.3f} R@P90={rows[-1]['recall@P>=0.90']:.2f}", flush=True)

        # Calibrated fusion: logistic regression on (STS-B CE, best cosines),
        # scored with 5-fold cross-validation so it is never tested on its
        # own training pairs.
        features = np.column_stack([
            fusion_inputs[variant]["STS-B CE (v1 rerank)"],
            fusion_inputs[variant]["BGE-base-v1.5"],
            fusion_inputs[variant]["MiniLM-L6 (v1 retrieval)"],
        ])
        folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=0)
        probs = cross_val_predict(
            LogisticRegression(max_iter=1000), features, y, cv=folds, method="predict_proba"
        )[:, 1]
        rows.append(evaluate("Fusion LR (CE + BGE + MiniLM), 5-fold CV", variant, y, probs))
        print(f"{variant:22s} {'Fusion LR (CV)':26s} AUC={rows[-1]['roc_auc']:.3f} R@P90={rows[-1]['recall@P>=0.90']:.2f}", flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(OUT, index=False)
    print()
    print(out.round(3).to_string(index=False))


if __name__ == "__main__":
    main()
