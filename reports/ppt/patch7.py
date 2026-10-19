"""Seventh pass: results, conclusion, implementation and formulation text for the deployed short-text setting
(Play Store R1 + RJ1 at t_low 0.40: P 0.834, R 0.351, F1 0.494; results/headline_short_text.txt)."""
import build as b

EDITS = {
    9: [("Precision 0.80", "Precision 0.83"),
        (" on human-labelled Play Store reviews.", " on human-labelled Play Store reviews (0.80 before the short-text setting)."),
        ("F1 0.46", "F1 0.49"),
        ("At equal precision (0.80):", "At precision 0.80 or more:"),
        (" 33% of duplicates found vs about 1% for BM25, MinHash and SimHash.",
         " 35% of duplicates found vs about 1% for BM25, MinHash and SimHash.")],
    12: [("On real reviews it reaches precision 0.80 and the highest F1 of every method tested, and it transfers unchanged to bug reports.",
          "On real reviews it reaches precision 0.83, recall 0.35 and F1 0.49, the highest of every method tested; a higher lower "
          "threshold for short-text channels improved precision and recall together while cutting LLM calls by about a quarter, "
          "and the same upper threshold transfers unchanged to bug reports (F1 0.78).")],
    7: [(" similarity ≥ 0.8306 joins automatically, &lt; 0.26 opens a new case; our 0.71 falls in between, so the LLM judge decides.",
         " similarity ≥ 0.8306 joins automatically; below t_low (0.40 for app reviews and chat, 0.26 for tickets) opens a new case; "
         "our 0.71 falls in between, so the LLM judge decides.")],
    20: [(" t_low = 20th percentile of similarities of true duplicate pairs  →  0.26 (80% of duplicates stay reachable).",
          " t_low = 20th percentile of similarities of true duplicate pairs  →  0.26 for tickets and bug reports; "
          "0.40 for short texts (app reviews, chat), confirmed on unseen apps.")],
    4: [("Two calibrated cuts: 0.26 and 0.8306", "Two calibrated cuts: t_low 0.26 / 0.40 and t_high 0.8306")],
}

for n, pairs in EDITS.items():
    s = b.rd(n)
    for old, new in pairs:
        assert s.count(old) == 1, (n, old)
        s = s.replace(old, new.replace("&lt;", "&lt;") if "&lt;" in old else new)
    b.wr(n, s)
print("ok")
