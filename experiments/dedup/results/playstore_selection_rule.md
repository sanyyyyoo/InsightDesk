# Pre-declared selection rule (written 2026-10-06 19:20, before Run 3 / merge results exist)

Fixed for every candidate: per product, wide band, exemplar retrieval (<= 5 diverse
exemplars per case), top-5 candidates, strict rule, judge sees each candidate case's raw
first complaint, gpt-oss-120b at temperature 0.

Candidates (development half = split seed 0, half B, 171 reviews):
  R1        vague rule v1 ("gated")              -- already run: P 0.779, R 0.468, F1 0.585
  R1+merge  R1 + periodic case-merge pass
  R3        corrected vague rule ("gated2")
  R3+merge  R3 + periodic case-merge pass

Rule: pick the candidate with the highest pairwise F1 on the development half, among
those whose precision is >= R1 precision - 0.03 (0.749). Ties (F1 within 0.005): fewer
LLM calls. The chosen configuration is then frozen and run ONCE on the untouched halves:
split seed 0 half A, split seed 1 halves B and A. Those numbers are the reported result.
Success target (unchanged): precision >= 0.85. Report whatever comes out.

# Addendum (written 2026-10-08 00:30, BEFORE the confirmation runs)

Candidate found on the development half (split 0 B): R1 + "top-1 agreement"
(--require-top1: an LLM merge is kept only if the chosen case is also the top
cosine candidate; otherwise new case). Dev: P 0.876, R 0.391, F1 0.540.
Because the rule was found on the dev half, it is confirmed ONCE, unchanged, on:
  (1) the three final halves (split 0 A, split 1 B, split 1 A)
  (2) leave-one-product-out (band calibrated on the other products)
Success = mean pairwise precision >= 0.85 on (1). Report whatever comes out;
no further changes to the rule after this run.
