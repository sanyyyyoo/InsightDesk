"""
List the 30 most similar report pairs from DIFFERENT GitBugs groups
(MiniLM cosine on the cleaned user text) for a manual label check.
Writes results/gitbugs_top30_crossgroup.csv; the manual verdicts are added
in the 'verdict' / 'reason' columns by hand.

  python experiments/dedup/gitbugs_label_check.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from backend.services.preprocess import clean_text  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "results", "gitbugs_top30_crossgroup.csv")


def main():
    from sentence_transformers import SentenceTransformer
    d = pd.read_csv("data/external/gitbugs_user.csv")
    e = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2").encode(
        d.complaint_text.map(clean_text).tolist(), normalize_embeddings=True)
    sims, groups = e @ e.T, d.issue_id.values
    iu = np.triu_indices(len(d), 1)
    cross = groups[iu[0]] != groups[iu[1]]
    a, b, s = iu[0][cross], iu[1][cross], sims[iu][cross]
    rows = []
    for rank, j in enumerate(np.argsort(-s)[:30], 1):
        i1, i2 = a[j], b[j]
        rows.append({"rank": rank, "cos": round(float(s[j]), 3),
                     "issue_a": d.issue_number[i1], "group_a": groups[i1],
                     "issue_b": d.issue_number[i2], "group_b": groups[i2],
                     "text_a": d.complaint_text[i1], "text_b": d.complaint_text[i2],
                     "verdict": "", "reason": ""})
        print(f"#{rank} cos={s[j]:.3f} A={d.issue_number[i1]} ({groups[i1]}) B={d.issue_number[i2]} ({groups[i2]})\n"
              f"  A: {d.complaint_text[i1][:230]!r}\n  B: {d.complaint_text[i2][:230]!r}")
    pd.DataFrame(rows).to_csv(OUT, index=False)


if __name__ == "__main__":
    main()
