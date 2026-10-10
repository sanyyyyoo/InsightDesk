"""
Independent recount of E5 (three-way decision) results.

e5_three_way.py saves every held-out run's case assignment
(results/[<data>_]e5_assignments_*.csv). This script joins them with the
ground-truth issue ids and recomputes pairwise precision / recall / F1
with scikit-learn's pair_confusion_matrix, then compares with the saved
metrics (results/[<data>_]e5_three_way_*.csv).

  python experiments/dedup/verify_e5.py [--data gitbugs_template]
"""

import argparse
import glob
import os
import sys

import pandas as pd
from sklearn.metrics.cluster import pair_confusion_matrix

sys.path.append(os.path.dirname(__file__))
from normalize import DATA_PATHS  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="synthetic", choices=list(DATA_PATHS))
    data = parser.parse_args().data
    prefix = "" if data == "synthetic" else f"{data}_"
    truth = pd.read_csv(DATA_PATHS[data]).set_index("complaint_ref")["issue_id"].astype(str)

    ok_all, n = True, 0
    for path in sorted(glob.glob(os.path.join(RESULTS, f"{prefix}e5_assignments_*.csv"))):
        if data == "synthetic" and os.path.basename(path).startswith(("gitbugs", "synthetic_")):
            continue
        assign = pd.read_csv(path)
        metrics = pd.read_csv(path.replace("e5_assignments_", "e5_three_way_"))
        print(f"\n=== {os.path.basename(path)}")
        print(f"{'judge':7s} run  |   TP    FP    FN | P recount / saved | R recount / saved | F1 recount / saved")
        for (judge, seed, half), g in assign.groupby(["judge", "split_seed", "held_out_half"], sort=False):
            (tn, fp), (fn, tp) = pair_confusion_matrix(truth.loc[g["complaint_ref"]].values, g["case"].values) // 2
            p = tp / (tp + fp) if tp + fp else 1.0
            r = tp / (tp + fn) if tp + fn else 0.0
            f = 2 * p * r / (p + r) if p + r else 0.0
            row = metrics[(metrics.judge == judge) & (metrics.split_seed == seed) & (metrics.held_out_half == half)].iloc[0]
            ok = all(abs(a - b) < 1e-9 for a, b in ((p, row.pair_precision), (r, row.pair_recall), (f, row.pair_f1)))
            ok_all &= ok
            n += 1
            print(f"{judge:7s} {seed}-{half}  | {tp:5d} {fp:5d} {fn:5d} | {p:.4f} / {row.pair_precision:.4f} | "
                  f"{r:.4f} / {row.pair_recall:.4f} | {f:.4f} / {row.pair_f1:.4f} {'OK' if ok else 'MISMATCH'}")
    print(f"\n{n} runs checked: " + ("ALL MATCH" if ok_all else "SOME DO NOT MATCH"))


if __name__ == "__main__":
    main()
