# Published duplicate finders on Play Store (pre-declared, written 2026-10-18 before running)
Methods: BM25 (REP's text core), Jaccard over 3-char shingles (what MinHash-LSH estimates), SimHash 64-bit.
Same input as InsightDesk (raw review text + product only; no labels, codebook, user IDs or metadata),
same time-ordered online assignment, same three held-out halves and pairwise scoring. Each method's
threshold is tuned on the tuning half for best F1 (generous to the baselines). Results reported as they fall.

Addendum 2026-10-18 (before running): equal-precision comparison. For each method, the threshold is the
one with the highest tuning-half recall among those with tuning-half precision >= 0.80 (InsightDesk's
operating level); if none reaches 0.80, the threshold with the highest tuning precision. Scored on the
held-out halves; reported as held-out precision and recall.
Addendum: Firefox 3 transfer - thresholds tuned on all Play Store reviews (best F1), applied unchanged to Firefox 3, as for InsightDesk.
