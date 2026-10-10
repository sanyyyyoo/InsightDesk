"""
Merge the team's re-check answers into the labels and build the final test set.

  round-1 labels : labelling/team_labels_v3_table.csv
  re-check       : labelling/recheck_done.xlsx (new_code; empty = keep)
Outputs:
  labelling/team_labels_round2.csv  - every person's codes after their own re-check
  labels/playstore_final_labels.csv - ONE code per review (450): overlap rows take
                                      the team's agreed code, others the owner's code
"""

import os

import pandas as pd

HERE = os.path.dirname(__file__)
LAB = os.path.join(HERE, "labelling")


def main():
    t = pd.read_csv(os.path.join(LAB, "team_labels_v3_table.csv"), keep_default_na=False)
    r = pd.read_excel(os.path.join(LAB, "recheck_done.xlsx"), header=11)
    r = r[r.labeller.notna()].copy()
    r["new_code"] = r.new_code.fillna("").astype(str).str.strip()
    codes = set(pd.read_csv(os.path.join(HERE, "labels", "playstore_codebook.csv")).problem_code)
    bad = r[(r.new_code != "") & ~r.new_code.isin(codes)]
    assert bad.empty, bad[["labeller", "row", "new_code"]]

    own = r[(r.labeller != "TEAM") & (r.new_code != "")]
    t2 = t.copy()
    key = ["labeller", "task", "row"]
    upd = own.set_index(key).new_code
    idx = t2.set_index(key).index
    hit = idx.isin(upd.index)
    t2.loc[hit, "problem_code"] = upd.reindex(idx[hit]).values
    changed = (t2.problem_code != t.problem_code)
    print(f"own re-check: {len(own)} answers, {int(changed.sum())} codes actually changed")
    print(t2.assign(ch=changed).groupby("labeller").ch.sum().to_dict())
    t2.to_csv(os.path.join(LAB, "team_labels_round2.csv"), index=False)

    team = r[r.labeller == "TEAM"].set_index("row").new_code
    assert (team != "").all()
    reviews = t2.drop_duplicates("row").set_index("row")[["product", "rating", "review_text"]]
    owner = t2[t2.task != "Overlap"].set_index("row").problem_code
    ov = t2[t2.task == "Overlap"].pivot(index="row", columns="labeller", values="problem_code")
    final, source = {}, {}
    for row in reviews.index:
        if row in ov.index:
            if row in team.index:
                final[row], source[row] = team[row], "team_agreed"
            else:
                final[row], source[row] = ov.loc[row].iloc[0], "all_three_same"
        else:
            final[row], source[row] = owner[row], "single_labeller"
    out = reviews.assign(problem_code=pd.Series(final), label_source=pd.Series(source)).reset_index()
    assert len(out) == 450 and (out.problem_code != "").all()
    out.to_csv(os.path.join(HERE, "labels", "playstore_final_labels.csv"), index=False)
    print(out.label_source.value_counts().to_dict())
    scored = out[~out.problem_code.isin({"other", "not_a_problem", "not_about_this_app"})
                 & ~out.problem_code.str.endswith("unspecified")]
    g = scored.groupby(["product", "problem_code"]).size()
    print(f"scored reviews {len(scored)} | duplicate groups (>=2) {int((g > 1).sum())} covering "
          f"{int(g[g > 1].sum())} reviews | duplicate pairs {int((g * (g - 1) // 2).sum())} | singletons {int((g == 1).sum())}")
    print("largest groups:", g.sort_values(ascending=False).head(8).to_dict())


if __name__ == "__main__":
    main()
