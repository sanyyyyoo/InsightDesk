"""
Independent check of the E2-E4 pipeline numbers.

For every held-out run saved in results/pipelines_*.csv (online-cos and
batch-cos), rebuild the run from scratch (same split seed, same tuned
threshold) and recompute the metrics with scikit-learn's
pair_confusion_matrix instead of compare_pipelines.evaluate. Prints the
raw pair counts so each number can be checked by hand:

    precision = TP / (TP + FP)      recall = TP / (TP + FN)
    F1        = 2PR / (P + R)

    python experiments/dedup/verify_results.py
"""

import glob
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics.cluster import pair_confusion_matrix

sys.path.append(os.path.dirname(__file__))

from compare_pipelines import batch_cos, online_cos  # noqa: E402  (clusterings only)
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def pair_counts(true, pred):
    # pair_confusion_matrix counts ordered pairs; halve for unordered pairs.
    (tn, fp), (fn, tp) = pair_confusion_matrix(true, pred) // 2
    return int(tp), int(fp), int(fn)


def main():
    import argparse
    from sentence_transformers import SentenceTransformer
    from normalize import DATA_PATHS, apply_text_mode

    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="synthetic", choices=list(DATA_PATHS))
    parser.add_argument("--model", default=MODEL)
    cli = parser.parse_args()
    data, model_id = cli.data, cli.model
    tag = model_id.replace("\\", "/").rstrip("/").split("/")[-1]
    prefix = "" if data == "synthetic" else f"{data}_"
    encoder = SentenceTransformer(model_id)
    detector = encoder if model_id == MODEL else SentenceTransformer(MODEL)
    base = load_ground_truth(path=DATA_PATHS[data])
    issues_all = np.array(base["issue_id"].astype(str).tolist())
    issue_ids = np.array(sorted(set(issues_all)))

    all_ok = True
    for path in sorted(glob.glob(os.path.join(RESULTS, f"pipelines_{prefix}{tag}*.csv"))):
        if data == "synthetic" and os.path.basename(path).startswith(("pipelines_synthetic_", "pipelines_gitbugs_")):
            continue   # other datasets' files share the prefix
        mode = os.path.basename(path)[len(f"pipelines_{prefix}{tag}"):-4].lstrip("_") or "raw"
        # boilerplate detection always uses plain MiniLM, exactly as compare_pipelines does
        df = base if mode == "raw" else apply_text_mode(base, mode, detector, data=data)
        emb = encoder.encode(df["cleaned_text"].tolist(), normalize_embeddings=True,
                             show_progress_bar=False)
        saved = pd.read_csv(path)
        print(f"\n=== text mode: {mode}  ({os.path.basename(path)}, {len(df)} complaints)")
        print(f"{'pipeline':10s} seed half   t   |   TP    FP    FN | P recomputed / saved | R recomputed / saved | F1 recomputed / saved")

        run_idx = 0
        for seed in [0, 1, 2, 3, 4]:
            rng = np.random.default_rng(seed)
            half = set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))
            a = np.where(np.isin(issues_all, list(half)))[0]
            b = np.where(~np.isin(issues_all, list(half)))[0]
            for h, test in (("B", b), ("A", a)):
                rows = saved[saved["split_seed"] == seed]
                for name, fn in (("online-cos", online_cos), ("batch-cos", batch_cos)):
                    row = rows[rows["pipeline"].str.startswith(name)].iloc[0 if h == "B" else 1]
                    t = float(row["threshold"])
                    pred = fn(emb[test], t)
                    tp, fp, fn_ = pair_counts(issues_all[test], pred)
                    p = tp / (tp + fp) if tp + fp else 1.0
                    r = tp / (tp + fn_)
                    f = 2 * p * r / (p + r) if p + r else 0.0
                    ok = all(abs(x - y) < 1e-9 for x, y in
                             ((p, row["pair_precision"]), (r, row["pair_recall"]), (f, row["pair_f1"])))
                    all_ok &= ok
                    print(f"{name:10s} {seed:4d}  {h}   {t:.2f} | {tp:5d} {fp:5d} {fn_:5d} | "
                          f"{p:.4f} / {row['pair_precision']:.4f}      | {r:.4f} / {row['pair_recall']:.4f}      | "
                          f"{f:.4f} / {row['pair_f1']:.4f} {'OK' if ok else 'MISMATCH'}")
                run_idx += 1

        summary = saved.groupby("pipeline")[["pair_precision", "pair_recall", "pair_f1"]].agg(["mean", "std"])
        print("\nMean ± sd over the 10 held-out runs (from the saved CSV):")
        print(summary.round(3).to_string())

    print("\nALL RUNS MATCH" if all_ok else "\nSOME RUNS DO NOT MATCH")


if __name__ == "__main__":
    main()
