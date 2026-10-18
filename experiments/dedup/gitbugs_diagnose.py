"""
Diagnostic (NOT a held-out result: uses labels on the full set) for the
GitBugs test set. Answers why the held-out protocol merges almost nothing:

  1. separability: ROC AUC of cosine for same-group vs different-group pairs
  2. retrieval: Recall@k - for each report whose group already has an
     earlier report, is one of them among the k most similar earlier reports?
     (the standard duplicate-bug-report metric)
  3. ceiling: best pairwise precision / recall / F1 over all thresholds for
     online and batch cosine, and the recall reachable at precision >= 0.85

  python experiments/dedup/gitbugs_diagnose.py
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score
from sklearn.metrics.cluster import pair_confusion_matrix

sys.path.append(os.path.dirname(__file__))
from compare_pipelines import batch_cos, online_cos  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "results", "gitbugs_diagnostic.csv")
VARIANTS = [("gitbugs_user", "raw"), ("gitbugs_template", "raw"), ("gitbugs_template", "boilerplate"),
            ("synthetic", "boilerplate")]


def prf(true, pred):
    (tn, fp), (fn, tp) = pair_confusion_matrix(true, pred) // 2
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def main():
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    rows = []
    for data, mode in VARIANTS:
        df = apply_text_mode(load_ground_truth(path=DATA_PATHS[data]), mode, enc, data=data)
        emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
        g = np.array(df["issue_id"].astype(str).tolist())
        sims = emb @ emb.T
        iu = np.triu_indices(len(g), 1)
        auc = roc_auc_score((g[:, None] == g[None, :])[iu], sims[iu])

        rec = {}
        for k in (1, 5, 10):
            hits = total = 0
            for i in range(1, len(g)):
                earlier_same = np.where(g[:i] == g[i])[0]
                if len(earlier_same) == 0:
                    continue
                total += 1
                top = np.argsort(-sims[i, :i])[:k]
                hits += bool(set(top) & set(earlier_same))
            rec[k] = hits / total

        best = {}
        for name, fn in (("online", online_cos), ("batch", batch_cos)):
            curve = [(t, *prf(g, fn(emb, t))) for t in np.round(np.arange(0.30, 0.96, 0.02), 2)]
            t, p, r, f = max(curve, key=lambda c: c[3])
            r85 = max([c[2] for c in curve if c[1] >= 0.85], default=0.0)
            best[name] = (t, p, r, f, r85)

        row = {"data": data, "text": mode, "reports": len(g), "groups": len(set(g)), "pair_auc": auc,
               "recall@1": rec[1], "recall@5": rec[5], "recall@10": rec[10]}
        for name, (t, p, r, f, r85) in best.items():
            row.update({f"{name}_best_t": t, f"{name}_best_P": p, f"{name}_best_R": r, f"{name}_best_F1": f,
                        f"{name}_R_at_P85": r85})
        rows.append(row)
        print(f"{data:17s} {mode:11s} AUC={auc:.3f} R@1={rec[1]:.2f} R@5={rec[5]:.2f} R@10={rec[10]:.2f} | "
              f"online best F1={best['online'][3]:.3f} (t={best['online'][0]}, P={best['online'][1]:.2f}, "
              f"R={best['online'][2]:.2f}), R@P>=.85={best['online'][4]:.2f} | batch best F1={best['batch'][3]:.3f} "
              f"(t={best['batch'][0]}, P={best['batch'][1]:.2f}, R={best['batch'][2]:.2f}), R@P>=.85={best['batch'][4]:.2f}",
              flush=True)
    pd.DataFrame(rows).to_csv(OUT, index=False)


if __name__ == "__main__":
    main()
