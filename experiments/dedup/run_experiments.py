"""
Run the Dedup v1 experiment grid offline and write results.

  python experiments/dedup/run_experiments.py

Outputs (experiments/dedup/results/):
  grid.csv            one row per (representation, top_k, threshold)
  order_sensitivity.csv  same configs replayed in shuffled arrival orders
"""

import os
import sys
import time

import pandas as pd

sys.path.append(os.path.dirname(__file__))

from replay_lab import (  # noqa: E402
    BASELINE_THRESHOLD, Models, Replay, case_metrics, load_ground_truth,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "results")

# Krisha's published Dedup v1 numbers at 0.5858 (threshold_replay_summary.csv)
EXPECTED_BASELINE = {"final_cases": 107, "contaminated_cases": 18, "cross_issue_assignments": 35}

REPRESENTATIONS = ["first", "medoid", "centroid", "multi"]
TOP_KS = [5, 10, 20]
THRESHOLDS = [0.50, BASELINE_THRESHOLD, 0.70]
ORDER_SEEDS = [1, 2, 3]


def run_one(df, emb, models, representation, top_k, threshold, label=""):
    t0 = time.time()
    replay = Replay(df, emb, models, representation, top_k, threshold).run()
    metrics = case_metrics(replay)
    metrics.update({
        "representation": representation, "top_k": top_k,
        "threshold": threshold, "order": label or "original",
        "seconds": round(time.time() - t0, 1),
    })
    print(
        f"{representation:9s} k={top_k:<3d} t={threshold:<7} {label:9s} "
        f"cases={metrics['final_cases']:3d} contam={metrics['contaminated_cases']:3d} "
        f"xissue={metrics['cross_issue_assignments']:3d} "
        f"pairP={metrics['pair_precision']:.3f} pairR={metrics['pair_recall']:.3f} "
        f"cov={metrics['mean_largest_case_coverage']:.3f} "
        f"retR={metrics['retrieval_recall']:.3f} ({metrics['seconds']}s)",
        flush=True,
    )
    return metrics


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    models = Models()

    df = load_ground_truth()
    emb = models.embed(df["cleaned_text"])
    print(f"{len(df)} complaints, {df['issue_id'].nunique()} issues\n", flush=True)

    # 1. Reproduce the frozen baseline before trusting any comparison.
    base = run_one(df, emb, models, "first", 5, BASELINE_THRESHOLD)
    mismatch = {k: (base[k], v) for k, v in EXPECTED_BASELINE.items() if base[k] != v}
    print("BASELINE REPRODUCED" if not mismatch else f"BASELINE MISMATCH {mismatch}", flush=True)

    # 2. Grid: one axis at a time is covered by the full grid.
    rows = [base]
    for representation in REPRESENTATIONS:
        for top_k in TOP_KS:
            for threshold in THRESHOLDS:
                if (representation, top_k, threshold) == ("first", 5, BASELINE_THRESHOLD):
                    continue
                rows.append(run_one(df, emb, models, representation, top_k, threshold))
                pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "grid.csv"), index=False)

    # 3. Arrival-order sensitivity at the baseline threshold.
    order_rows = []
    for seed in ORDER_SEEDS:
        shuffled = load_ground_truth(order_seed=seed)
        shuffled_emb = models.embed(shuffled["cleaned_text"])
        for representation in REPRESENTATIONS:
            order_rows.append(run_one(
                shuffled, shuffled_emb, models, representation, 5,
                BASELINE_THRESHOLD, label=f"seed{seed}",
            ))
            pd.DataFrame(order_rows).to_csv(os.path.join(OUT_DIR, "order_sensitivity.csv"), index=False)

    print("\nDone. Results in", OUT_DIR)


if __name__ == "__main__":
    main()
