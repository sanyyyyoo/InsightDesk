"""
Real-data test set from the team's Play Store labels.

  issue_id = product | problem_code   (same product + same code = duplicates)
  Unscored codes never count as duplicates of each other:
    other, not_a_problem, not_about_this_app, *_unspecified, and
    missing_features_vs_web (team: means "some feature is missing" in
    general, i.e. a topic - different missing features need different fixes).
  complaint_ref = chronological order of the review (realistic stream).

Outputs (data/external/, local only):
  playstore_scored.csv  primary: scored reviews only
  playstore_all.csv     strict: all 450, unscored reviews as one-offs
"""

import os

import pandas as pd

HERE = os.path.dirname(__file__)
UNSCORED = {"other", "not_a_problem", "not_about_this_app", "missing_features_vs_web"}


def main():
    lab = pd.read_csv(os.path.join(HERE, "labels", "playstore_final_labels.csv"))
    key = pd.read_excel(os.path.join(HERE, "labelling", "playstore_labelling_sheet_v2.xlsx"),
                        sheet_name="All_rows_key")[["row", "complaint_id"]]
    raw = pd.read_csv("data/play_store_reviews.csv")[["complaint_id", "complaint_text", "created_at"]]
    d = lab.merge(key, on="row").merge(raw, on="complaint_id")
    assert len(d) == 450
    assert (d.review_text.str.split().str.join(" ") == d.complaint_text.str.split().str.join(" ")).all()
    scored = ~d.problem_code.isin(UNSCORED) & ~d.problem_code.str.endswith("unspecified")
    d["issue_id"] = (d["product"] + "|" + d.problem_code).where(scored, "lone_" + d.row.astype(str))
    d["scored"] = scored
    d = d.sort_values(["created_at", "row"]).reset_index(drop=True)
    d["complaint_ref"] = range(1, len(d) + 1)
    d["department"] = d["product"]
    cols = ["complaint_ref", "department", "issue_id", "complaint_text", "created_at", "row", "problem_code", "scored"]
    os.makedirs("data/external", exist_ok=True)
    d[cols].to_csv("data/external/playstore_all.csv", index=False)
    s = d[d.scored].copy()
    s["complaint_ref"] = range(1, len(s) + 1)
    s[cols].to_csv("data/external/playstore_scored.csv", index=False)
    for name, x in (("all", d), ("scored", s)):
        g = x.issue_id.value_counts()
        print(f"{name:7s} reviews {len(x)} | groups>=2 {int((g > 1).sum())} | pairs {int((g * (g - 1) // 2).sum())} "
              f"| one-offs {int((g == 1).sum())} | products {x.department.nunique()}")


if __name__ == "__main__":
    main()
