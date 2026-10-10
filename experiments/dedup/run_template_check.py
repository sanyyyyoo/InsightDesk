"""
Round 2: does the evaluation data (generator stock phrases) hide the
effect of case representation?

Same replay and metrics as run_experiments.py, on the synthetic ground
truth with generator openers/closers removed (evaluation-data fix only).

  python experiments/dedup/run_template_check.py
"""

import os
import sys

import pandas as pd

sys.path.append(os.path.dirname(__file__))

from replay_lab import Models, load_ground_truth  # noqa: E402
from run_experiments import OUT_DIR, run_one  # noqa: E402

REPRESENTATIONS = ["first", "medoid", "centroid"]
THRESHOLDS = [0.30, 0.40, 0.50, 0.5858, 0.70]
ORDER_SEEDS = [None, 1, 2, 3]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    models = Models()
    rows = []

    for seed in ORDER_SEEDS:
        df = load_ground_truth(order_seed=seed, strip_templates=True)
        emb = models.embed(df["cleaned_text"])
        label = "original" if seed is None else f"seed{seed}"
        # Full threshold sweep in the original order, 2 key thresholds when shuffled.
        thresholds = THRESHOLDS if seed is None else [0.40, 0.5858]

        for representation in REPRESENTATIONS:
            for threshold in thresholds:
                metrics = run_one(df, emb, models, representation, 5, threshold, label=label)
                metrics["data"] = "templates_removed"
                rows.append(metrics)
                pd.DataFrame(rows).to_csv(os.path.join(OUT_DIR, "templates_removed.csv"), index=False)

    print("\nDone. Results in", OUT_DIR)


if __name__ == "__main__":
    main()
