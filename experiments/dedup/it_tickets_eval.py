"""
IT-ticket sanity check (rule: D:/PBL/InsightDesk-claude-review/reports/it_tickets/it_tickets_rule.md).

Cross-topic error floor for R1 (app replay) and the main-branch pipeline
(MiniLM + MS-MARCO cross-encoder, -2.21) on the same 1,000 IT tickets.
A merged pair / case whose tickets carry different topic labels is almost
surely wrong; same-topic merges are NOT counted as right (topics are coarse).

  python experiments/dedup/it_tickets_eval.py
"""

import itertools
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from backend.services.preprocess import clean_text  # noqa: E402

SAMPLE = "data/external/it_tickets/it_tickets_sample1000.csv"
R1 = "D:/PBL/InsightDesk-claude-review/reports/it_tickets/replay_assignments.csv"
SAVED = "data/external/it_tickets/production_assignments.csv"
B, SEED = 2000, 11


def floor(case, topic):
    """Cross-topic share of merged pairs and of multi-ticket cases."""
    df = pd.DataFrame({"c": case, "t": topic})
    pairs = cross = 0
    multi = mixed = 0
    for _, g in df.groupby("c"):
        if len(g) < 2:
            continue
        multi += 1
        mixed += g.t.nunique() > 1
        for x, y in itertools.combinations(g.t, 2):
            pairs += 1
            cross += x != y
    return pairs, cross, multi, mixed


def main():
    s = pd.read_csv(SAMPLE)
    if os.path.exists(SAVED):
        prod = pd.read_csv(SAVED).production.to_numpy()
    else:
        from replay_lab import Models, Replay
        from sentence_transformers import CrossEncoder
        d = s.copy()
        d["issue_id"] = d.topic
        d["cleaned_text"] = d.complaint_text.astype(str).map(clean_text)
        models = Models()
        models.cross_encoder, models._ce_cache = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2"), {}
        rep = Replay(d, models.embed(d["cleaned_text"]), models, "first", 5, -2.21).run()
        prod = pd.Series(rep.case_of_row).sort_index().to_numpy()
        pd.DataFrame({"row": range(len(prod)), "production": prod}).to_csv(SAVED, index=False)
    r1 = pd.read_csv(R1).set_index("row").case_id.reindex(range(len(s))).to_numpy()
    rows = []
    for name, case in (("main branch (MS-MARCO -2.21)", prod), ("R1 (app, real judge)", r1)):
        pairs, cross, multi, mixed = floor(case, s.topic.to_numpy())
        rng = np.random.default_rng(SEED)
        cases = pd.unique(case)
        boot = []
        for _ in range(B):                        # bootstrap over cases for the pair-level floor
            pick = rng.choice(cases, len(cases))
            p = c = 0
            for cid in pick:
                t = s.topic.to_numpy()[case == cid]
                n = len(t)
                if n > 1:
                    p += n * (n - 1) / 2
                    c += n * (n - 1) / 2 - sum(k * (k - 1) / 2 for k in pd.Series(t).value_counts())
            boot.append(c / p if p else 0)
        lo, hi = np.percentile(boot, [2.5, 97.5])
        size = pd.Series(case).value_counts()
        rows.append({"pipeline": name, "cases": len(size), "multi-ticket cases": multi,
                     "largest case": int(size.max()), "merged pairs": pairs,
                     "cross-topic pairs (error floor)": f"{cross / pairs:.3f} [{lo:.3f},{hi:.3f}]" if pairs else "-",
                     "mixed-topic cases": f"{mixed}/{multi} ({mixed / multi:.0%})" if multi else "-"})
    print(pd.DataFrame(rows).to_string(index=False))


if __name__ == "__main__":
    main()
