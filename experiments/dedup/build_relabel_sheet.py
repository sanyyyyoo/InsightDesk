"""
Blind re-labelling sheet for the failure audit (bucket D = suspected label errors).

Items: every review in a case that the unseen-company run (agreement rule)
contaminated - the 19 reviews that landed in a case with a different problem
AND the members of those cases - plus a random set of control (one third as many)
reviews from the rest, so labellers cannot tell which reviews are disputed.

Blind: each row shows only the app and the review text - no earlier label,
no system decision. All three people label every review independently; the
majority code becomes the corrected label (ties are discussed). Any change
is applied to the scores of EVERY method, not only the pipeline.

Outputs (local only):
  labelling/relabel_sheet.xlsx   one tab, instructions on top, codes on the right
  labelling/relabel_key.csv      row -> complaint_ref, role (audit / control), old code

  python experiments/dedup/build_relabel_sheet.py

Option A (every scored review triple-labelled): --remaining builds the same
sheet for all scored reviews NOT in the first relabel sheet:
  labelling/relabel_sheet_rest.xlsx, labelling/relabel_key_rest.csv
"""

import argparse
import os

import numpy as np
import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

HERE = os.path.dirname(__file__)
RES = os.path.join(HERE, "results")
RUN = os.path.join(RES, "playstore_e5_assignments_llm_perproduct_wideband_exemplars_top5_top1agree_founder_gated_lopo.csv")
CODEBOOK = os.path.join(HERE, "labels", "playstore_codebook.csv")
OUT = os.path.join(HERE, "labelling", "relabel_sheet.xlsx")
KEY = os.path.join(HERE, "labelling", "relabel_key.csv")
LABELLERS = ["Sanyogita", "Krisha", "Krushnam"]
SEED = 8
HEADER_ROW = 9
CODE_COL = 10                     # column J

INSTRUCTIONS = [
    "Re-label check - pick the SPECIFIC problem of each review. About 10-15 minutes.",
    "Do ALL rows yourself, alone (filter column A to your name). Do not look at the others' answers.",
    "Judge only the text you see. There are no right answers hidden here: we compare the three of you.",
    "RULE 1: no failure at all ('Very bad', 'Waste app') -> not_a_problem.   RULE 2: 'other' only when no listed code fits.",
    "RULE 3: *_unspecified only when the review names NO symptom. Two problems -> the main one; the other code in notes.",
    "Codes with definitions and example rows are on the right (column J onwards).",
]
COLS = ["labeller", "item", "product", "review_text", "problem_code", "confidence", "notes"]
WIDTHS = {"labeller": 12, "item": 6, "product": 11, "review_text": 80, "problem_code": 30, "confidence": 11, "notes": 28}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--remaining", action="store_true")
    args = ap.parse_args()
    out, key = (OUT.replace(".xlsx", "_rest.xlsx"), KEY.replace(".csv", "_rest.csv")) if args.remaining else (OUT, KEY)
    d = pd.read_csv("data/external/playstore_scored.csv").set_index("complaint_ref")
    a = pd.read_csv(RUN).drop_duplicates(["held_out_half", "complaint_ref"], keep="last")
    a = a.join(d[["problem_code"]], on="complaint_ref")
    audit = set()
    for _, g in a.groupby(["held_out_half", "case"]):
        if g.problem_code.nunique() > 1:                 # contaminated case: all its members
            audit |= set(g.complaint_ref)
    rest = sorted(set(d.index) - audit)
    controls = set(np.random.default_rng(SEED).choice(rest, size=round(len(audit) / 3), replace=False).tolist())
    items = pd.DataFrame({"complaint_ref": sorted(audit | controls)})
    items["role"] = np.where(items.complaint_ref.isin(audit), "audit", "control")
    if args.remaining:                      # everything the first relabel sheet did not cover
        done = set(pd.read_csv(KEY).complaint_ref)
        items = pd.DataFrame({"complaint_ref": sorted(set(d.index) - done), "role": "rest"})
        INSTRUCTIONS[0] = (f"Re-label (part 2) - pick the SPECIFIC problem of each review. {len(items)} reviews, "
                           f"about {round(len(items) * 12 / 60 / 5) * 5} minutes; you can stop and continue later.")
    items = items.sample(frac=1, random_state=SEED).reset_index(drop=True)   # audit and controls mixed
    items["item"] = range(1, len(items) + 1)
    items = items.join(d[["department", "complaint_text", "problem_code"]], on="complaint_ref")

    t = pd.concat([items.assign(labeller=n) for n in LABELLERS], ignore_index=True)
    t = t.rename(columns={"department": "product", "complaint_text": "review_text"})
    t["problem_code"], t["confidence"], t["notes"] = "", "", ""
    t = t[COLS]

    codes = pd.read_csv(CODEBOOK)
    wb = Workbook()
    ws = wb.active
    ws.title = "Relabel"
    blue = PatternFill("solid", fgColor="1F5FA8")
    fill_in = PatternFill("solid", fgColor="FFF7DC")
    thin = Border(top=Side(style="thin", color="1F5FA8"))
    for i, line in enumerate(INSTRUCTIONS, 1):
        ws.cell(i, 1, line).font = Font(bold=(i == 1 or line.startswith("RULE")), size=12 if i == 1 else 10,
                                        color="1F5FA8" if i == 1 else "000000")
        ws.merge_cells(start_row=i, start_column=1, end_row=i, end_column=len(COLS))
    for j, c in enumerate(COLS, 1):
        cell = ws.cell(HEADER_ROW, j, c)
        cell.font, cell.fill = Font(bold=True, color="FFFFFF"), blue
        ws.column_dimensions[get_column_letter(j)].width = WIDTHS[c]
    first, last = HEADER_ROW + 1, HEADER_ROW + len(t)
    prev = None
    for i, rec in enumerate(t.itertuples(index=False), first):
        for j, v in enumerate(rec, 1):
            cell = ws.cell(i, j, v)
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if COLS[j - 1] in ("problem_code", "confidence", "notes"):
                cell.fill = fill_in
        if prev is not None and rec.labeller != prev:
            for j in range(1, len(COLS) + 1):
                ws.cell(i, j).border = thin
        prev = rec.labeller
    ws.auto_filter.ref = f"A{HEADER_ROW}:{get_column_letter(len(COLS))}{last}"
    ws.freeze_panes = f"A{HEADER_ROW + 1}"

    code_cols = ["problem_code", "area", "definition", "example_rows"]
    for j, c in enumerate(code_cols, CODE_COL):
        cell = ws.cell(HEADER_ROW, j, c)
        cell.font, cell.fill = Font(bold=True, color="FFFFFF"), blue
        ws.column_dimensions[get_column_letter(j)].width = {"definition": 60, "problem_code": 28}.get(c, 16)
    for i, rec in enumerate(codes[code_cols].fillna("").itertuples(index=False), HEADER_ROW + 1):
        for j, v in enumerate(rec, CODE_COL):
            ws.cell(i, j, v).alignment = Alignment(wrap_text=True, vertical="top")
    ws.column_dimensions[get_column_letter(CODE_COL - 1)].width = 3
    L = get_column_letter(CODE_COL)
    dv_code = DataValidation(type="list", allow_blank=True, showErrorMessage=True,
                             formula1=f"${L}${HEADER_ROW + 1}:${L}${HEADER_ROW + len(codes)}",   # no leading '='
                             errorTitle="Unknown code", error="Pick a code from the list.")
    dv_conf = DataValidation(type="list", formula1='"sure,unsure"', allow_blank=True)
    ws.add_data_validation(dv_code)
    ws.add_data_validation(dv_conf)
    pc, cf = (get_column_letter(COLS.index(c) + 1) for c in ("problem_code", "confidence"))
    dv_code.add(f"{pc}{first}:{pc}{last}")
    dv_conf.add(f"{cf}{first}:{cf}{last}")
    wb.save(out)
    items[["item", "complaint_ref", "role", "department", "problem_code"]].rename(
        columns={"problem_code": "old_code"}).to_csv(key, index=False)

    # checks: blind (no old codes in the sheet), balanced, every audit review present
    assert "old" not in " ".join(COLS)
    print(f"audit reviews (all members of contaminated cases): {len(audit)} | controls: {len(controls)} "
          f"| items: {len(items)} | rows per person: {len(items)} | sheet rows: {len(t)}")
    print(items.groupby(["department", "role"]).size().unstack(fill_value=0))
    print("saved", out, "and key", key)


if __name__ == "__main__":
    main()
