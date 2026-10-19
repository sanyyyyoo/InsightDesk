"""Sixth pass: problem statement for the current system, calibration table without the 'original' row,
table of contents, and presentation order."""
import re
from xml.sax.saxutils import escape

import build as b
import patch3 as p3

PROBLEM = [
    "Help-desk software companies such as Vision Helpdesk receive complaints from app reviews, support tickets, chat and "
    "web forms. The same problem is reported many times in different words, so agents triage it again and again, and no one "
    "sees how many customers a single problem affects.",
    "Existing tools group complaints by theme (“login”) rather than by problem (“the OTP never arrives”): keyword rules and "
    "topic models mix different problems, and a single similarity threshold either merges unrelated complaints or misses "
    "paraphrases. Feedback tools flag spikes with z-scores on whole categories, which miss a new problem growing from a low base.",
    "There is a need for a system that groups raw complaints into problem-level cases as they arrive with high precision, "
    "tracks each case’s volume to raise incidents early, adds sentiment, topic and root cause, and routes each incident to "
    "the responsible department after a person approves it.",
]

TOC = ["Problem Statement", "Literature Survey", "Objectives", "Flow Diagram", "Implementation & Formulation",
       "Datasets & Calibration", "Results", "Applications & Future Scope", "Conclusion & References"]

# presentation order, by slide file number
ORDER = [1, 2, 3, 4, 16, 17, 5, 6, 7, 8, 20, 24, 23, 21, 22, 9, 18, 19, 10, 11, 12, 13, 14, 15]


def problem_old():
    s = b.rd(3)
    nm = [n for n in re.findall(r'name="(Google Shape;\d+;p\d+)"', s)
          if "Vision Helpdesk handles" in s[b.shape_block(s, n)[0]:b.shape_block(s, n)[1]]][0]
    b.wr(3, b.set_paras(s, nm, [b.plain(t, 1500, False, "just", 900) for t in PROBLEM]))


def toc():
    s = b.rd(2)
    rows = re.findall(r"<a:tr .*?</a:tr>", s, re.S)
    assert len(rows) == 10
    for k, (row, label) in enumerate(zip(rows[1:], TOC), 1):
        new = row
        for cell, text in zip(re.findall(r"<a:tc.*?</a:tc>", row, re.S), (f"{k}.", label)):
            seen = []

            def put(m):
                seen.append(1)
                return f"<a:t>{escape(text) if len(seen) == 1 else ''}</a:t>"
            new = new.replace(cell, re.sub(r"<a:t>[^<]*</a:t>", put, cell), 1)
        s = s.replace(row, new, 1)
    b.wr(2, s)


def calibration():
    s = b.rd(21)
    s = re.sub(r'<p:sp><p:nvSpPr><p:cNvPr id="960" name="Results text 960".*?</p:sp>', "", s, flags=re.S)
    b.wr(21, s)
    p3.table_slide(21, "THRESHOLD CALIBRATION & SENSITIVITY",
                   [2450000, 1300000, 1350000, 850000, 750000, 650000, 750000],
                   ["Setting", "t_low", "t_high", "Precision", "Recall", "F1", "LLM share"],
                   [["Short-text setting (deployed)", "0.40", "0.8306", "0.883", "0.284", "0.430", "66%"],
                    ["Long-text setting (tickets, bug reports)", "0.26", "0.8306", "0.810", "0.259", "0.392", "86%"],
                    ["t_low ≈ 0.30", "0.26 + 0.04", "0.8306", "0.803", "0.256", "0.388", "81%"],
                    ["t_low ≈ 0.35", "0.26 + 0.09", "0.8306", "0.867", "0.264", "0.404", "71%"],
                    ["t_high lowered by 0.08", "0.26", "≈ 0.75", "0.808", "0.277", "0.413", "78%"],
                    ["Unseen apps: 0.26 → 0.40", "0.26 → 0.40", "0.8306", "0.608 → 0.635", "0.284 → 0.255", "–", "94% → 77%"],
                    ["Bug reports: 0.26 → 0.40", "0.26 → 0.40", "0.8306", "0.908 → 0.912", "0.578 → 0.571", "–", "96% → 90%"]],
                   360000,
                   "Play Store held-out halves pooled, live judge calls. t_high = 0.8306 (lowest similarity at which tuning pairs "
                   "are ≥ 97% true duplicates) is used for every channel; t_low is 0.40 for app reviews and chat and 0.26 for tickets "
                   "and bug reports, where raising it changed little. Before re-joining (see results).")


def order():
    p = open(f"{b.U}/presentation.xml", encoding="utf8").read()
    rels = open(f"{b.U}/_rels/presentation.xml.rels", encoding="utf8").read()
    rid = {}
    for m in re.finditer(r"<Relationship [^>]*>", rels):
        t = re.search(r'Target="slides/slide(\d+)\.xml"', m.group(0))
        if t:
            rid[int(t.group(1))] = re.search(r'Id="(rId\d+)"', m.group(0)).group(1)
    ids = {re.search(r'r:id="(rId\d+)"', x).group(1): x for x in re.findall(r"<p:sldId [^>]*/>", p)}
    assert sorted(ORDER) == sorted(rid) and len(ids) == len(ORDER)
    lst = "".join(ids[rid[n]] for n in ORDER)
    p = re.sub(r"(<p:sldIdLst>).*?(</p:sldIdLst>)", lambda m: m.group(1) + lst + m.group(2), p, flags=re.S)
    open(f"{b.U}/presentation.xml", "w", encoding="utf8").write(p)


def main():
    pass  # problem statement: replaced in place on slide 3 (text box Google Shape;61;p10)
    toc()
    calibration()
    order()
    print("ok")


if __name__ == "__main__":
    main()
