"""
Krisha's second-round questions (after the PDF).

Q3  How was the 0.976 Top-5 retrieval recall measured? Recompute it in the
    same sequential v1 replay (STS-B 0.5858, founder, Top-5, published order)
    under two definitions, both using the GENERATOR issue_id (never the case
    the complaint is eventually assigned to):
      lenient  a retrieved case counts if ANY of its members has the query's issue
               (the definition replay_lab.py used for 0.976)
      strict   a retrieved case counts only if its MAJORITY issue is the query's
               issue (and the founder's issue, reported separately)
    Denominator: queries for which such a case already exists.

Q4  Is 0.28-0.30 (150-pair calibration recall at 0.6469) vs 0.20 (replay
    pairwise recall) consistent? Score pair-by-pair with STS-B:
      - the 75 calibration duplicates (her set)
      - ALL 4,156 within-issue pairs of the 488 complaints
    and compare with the replay's pairwise recall at the same thresholds.

  python experiments/dedup/krisha_q_round2.py
"""

import itertools
import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from replay_lab import Models, Replay, case_metrics, load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")


class AuditReplay(Replay):
    """Same replay; additionally records strict retrieval hits before each decision."""

    def _candidates(self, row):
        cand, scores = super()._candidates(row)
        issues = self.df["issue_id"].astype(str).values
        q = issues[row]
        maj = {}
        for c in self.cases:
            maj[c.index] = Counter(issues[c.member_rows]).most_common(1)[0][0]
        any_case = {c.index for c in self.cases if any(issues[r] == q for r in c.member_rows)}
        maj_case = {i for i, m in maj.items() if m == q}
        founder_case = {c.index for c in self.cases if issues[c.member_rows[0]] == q}
        self.audit.append({
            "row": row, "issue": q,
            "lenient_exists": bool(any_case), "lenient_hit": bool(any_case & set(cand)),
            "strict_exists": bool(maj_case), "strict_hit": bool(maj_case & set(cand)),
            "founder_exists": bool(founder_case), "founder_hit": bool(founder_case & set(cand)),
        })
        return cand, scores

    def run(self):
        self.audit = []
        return super().run()


def main():
    models = Models()
    df = load_ground_truth()

    # ---------------- Q3
    rep = AuditReplay(df, models.embed(df["cleaned_text"]), models, "first", 5, 0.5858).run()
    a = pd.DataFrame(rep.audit)
    cm = case_metrics(rep)
    print(f"Q3  replay check: cases={cm['final_cases']} contaminated={cm['contaminated_cases']} "
          f"cross-issue={cm['cross_issue_assignments']}  (published: 107 / 18 / 35)")
    for kind in ("lenient", "strict", "founder"):
        sub = a[a[f"{kind}_exists"]]
        print(f"    {kind:8s} Top-5 retrieval recall = {sub[f'{kind}_hit'].mean():.3f}  "
              f"({int(sub[f'{kind}_hit'].sum())}/{len(sub)} queries)")

    # ---------------- Q4
    ce = models.cross_encoder
    cal = pd.read_csv("data/calibration_pairs.csv")
    pos = cal[cal.true_label == "duplicate"]
    s_cal = np.asarray(ce.predict([(clean_text(x), clean_text(y)) for x, y in zip(pos.text_a, pos.text_b)],
                                  show_progress_bar=False))
    pairs = [(i, j) for _, g in df.groupby("issue_id") for i, j in itertools.combinations(g.index, 2)]
    ct = df["cleaned_text"].values
    uniq = {}
    for i, j in pairs:
        uniq.setdefault((ct[i], ct[j]), None)
    keys = list(uniq)
    scores = np.asarray(ce.predict(keys, show_progress_bar=False, batch_size=64))
    lookup = dict(zip(keys, scores))
    s_all = np.array([lookup[(ct[i], ct[j])] for i, j in pairs])
    print(f"\nQ4  within-issue pairs: {len(pairs)} ({len(keys)} unique text pairs scored)")
    rows = []
    for t in (0.5858, 0.6469):
        r = {"threshold": t,
             "calibration_75_pairs_recall": float((s_cal >= t).mean()),
             "all_4156_pairs_recall_pairwise_scored": float((s_all >= t).mean())}
        rep_t = Replay(df, models.embed(df["cleaned_text"]), models, "first", 5, t).run()
        r["replay_pairwise_recall"] = case_metrics(rep_t)["pair_recall"]
        rows.append(r)
        print("   ", {k: round(v, 3) for k, v in r.items()})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "krisha_q4_recall_populations.csv"), index=False)
    a.to_csv(os.path.join(RESULTS, "krisha_q3_retrieval_audit.csv"), index=False)


if __name__ == "__main__":
    main()
