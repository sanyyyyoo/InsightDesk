"""
E8: multiple complaint-level exemplars per case (no LLM).

Does representing a case by several member complaints, instead of only its
first complaint, let real duplicates reach the shortlist?

  founder    case = its first complaint (current design)
  all        case scored by its best-matching member (max over all members)
  diverse    case keeps up to MAX_EX exemplars; a new member becomes an
             exemplar only if it is not a near-copy (< DIVERSE_SIM) of one
             already kept, so one case can cover several phrasings

Per product, held-out protocol (5 splits x 2 halves), wide band from the
tuning half (as e5_three_way --band wide). Two deciders:
  single  merge if best score >= t (t tuned on the tuning half, P >= 0.90)
  oracle  perfect judge over the top-3 shortlisted cases in the band
The oracle shows the ceiling each representation allows; single shows the
risk (one stray member can attract unrelated complaints = chaining).

  python experiments/dedup/e8_exemplars.py --data playstore
"""

import argparse
import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))

from compare_pipelines import SPLIT_SEEDS, evaluate  # noqa: E402
from e5_three_way import MAX_CANDIDATES, band_thresholds_wide  # noqa: E402
from normalize import DATA_PATHS  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

OUT_DIR = os.path.join(os.path.dirname(__file__), "results")
MAX_EX = 5
DIVERSE_SIM = 0.85
GRID = np.round(np.arange(0.30, 0.96, 0.02), 3)


def assign(emb, rows, method, decide, t_high=None, t_low=None, t=None, issues=None):
    """Online assignment of rows; returns labels aligned with rows."""
    exemplars, members = [], []          # per case: list of row ids
    labels = np.empty(len(rows), dtype=np.int64)
    for k, i in enumerate(rows):
        if exemplars:
            scores = np.array([float(np.max(emb[ex] @ emb[i])) for ex in exemplars])
            order = np.argsort(-scores)
            chosen = -1
            if decide == "single":
                if scores[order[0]] >= t:
                    chosen = int(order[0])
            else:                                   # oracle judge on the band
                if scores[order[0]] >= t_high:
                    chosen = int(order[0])
                else:
                    for c in order[:MAX_CANDIDATES]:
                        if scores[c] < t_low:
                            break
                        vals, cnt = np.unique(issues[members[c]], return_counts=True)
                        if vals[cnt.argmax()] == issues[i]:
                            chosen = int(c)
                            break
            if chosen >= 0:
                labels[k] = chosen
                members[chosen].append(i)
                ex = exemplars[chosen]
                if method == "all":
                    ex.append(i)
                elif method == "diverse" and len(ex) < MAX_EX and np.max(emb[ex] @ emb[i]) < DIVERSE_SIM:
                    ex.append(i)
                continue
        exemplars.append([i])
        members.append([i])
        labels[k] = len(exemplars) - 1
    return labels


def per_group(fn, rows, groups):
    labels = np.empty(len(rows), dtype=np.int64)
    offset = 0
    for g in pd.unique(groups[rows]):
        pos = np.where(groups[rows] == g)[0]
        lab = fn(rows[pos])
        labels[pos] = lab + offset
        offset += lab.max() + 1
    return labels


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="playstore", choices=list(DATA_PATHS))
    args = parser.parse_args()
    from sentence_transformers import SentenceTransformer
    df = load_ground_truth(path=DATA_PATHS[args.data])
    emb = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2").encode(
        df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    issue_ids = np.array(sorted(set(issues)))

    out = []
    for seed in SPLIT_SEEDS:
        rng = np.random.default_rng(seed)
        half = set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))
        a = np.where(np.isin(issues, list(half)))[0]
        b = np.where(~np.isin(issues, list(half)))[0]
        for h, (tune, test) in (("B", (a, b)), ("A", (b, a))):
            t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], groups[tune])
            for method in ("founder", "all", "diverse"):
                # single threshold tuned on the tuning half with the same representation
                best_t, best_f1 = GRID[-1], -1.0
                for t in GRID:
                    lab = per_group(lambda r: assign(emb, r, method, "single", t=t), tune, groups)
                    m = evaluate(lab, issues[tune], np.arange(len(tune)))
                    if m["pair_precision"] >= 0.90 and m["pair_f1"] > best_f1:
                        best_t, best_f1 = t, m["pair_f1"]
                for decide in ("single", "oracle"):
                    lab = per_group(lambda r: assign(emb, r, method, decide, t_high, t_low, best_t, issues), test, groups)
                    m = evaluate(lab, issues[test], np.arange(len(test)))
                    m.update({"method": method, "decider": decide, "split_seed": seed, "held_out_half": h,
                              "t": best_t if decide == "single" else np.nan, "t_low": t_low, "t_high": t_high})
                    out.append(m)
                    print(f"seed={seed} {h} {method:8s} {decide:6s} P={m['pair_precision']:.3f} "
                          f"R={m['pair_recall']:.3f} F1={m['pair_f1']:.3f} contam={m['contaminated_cases']}", flush=True)
    res = pd.DataFrame(out)
    res.to_csv(os.path.join(OUT_DIR, f"e8_exemplars_{args.data}.csv"), index=False)
    print("\n", res.groupby(["decider", "method"])[["pair_precision", "pair_recall", "pair_f1", "contaminated_cases"]]
          .agg(["mean", "std"]).round(3).to_string())


if __name__ == "__main__":
    main()
