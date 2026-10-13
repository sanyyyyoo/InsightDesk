# Auto-generated taxonomy + classification: pre-declared rule (2026-10-12, before any run)

Question: can an LLM-built problem list ("taxonomy"), made automatically from a
company's PAST complaints (no human codebook), group NEW complaints better than
open-ended dedup (R1)?

Data, no leakage:
- history (taxonomy input): the real Play Store reviews of the 1,432 set that are
  NOT among the 450 team-labelled reviews (~494 reviews), per company;
- test: the 338 scored team-labelled reviews (answer key = team labels, never
  shown to the LLM; the team codebook is not used anywhere in the method).

Method (gpt-oss-120b, temperature 0, JSON; same model as the R1 judge):
1. Taxonomy per company: the LLM reads the company's history in chunks of 40
   reviews and keeps an updated list of SPECIFIC problems (code + one-line
   definition naming feature and symptom); reviews with no concrete symptom do
   not create codes; at most 50 codes per company. Built once, then frozen.
2. Classification: each test review (10 per call, its own company's list) gets
   one code, or "none" (a concrete problem not in the list) or "vague".
3. Grouping: same company + same code = same case; "none" and "vague" =
   singletons (T-LLM). Secondary, approximate hybrid (T+R1): for pairs of two
   "none" reviews, use R1's existing held-out case decision instead.
4. No-LLM variant (T-emb): nearest taxonomy definition by MiniLM cosine, if
   >= 0.50, else "none" (threshold fixed now, not tuned).

Scoring: pairwise P / R / F1 over the same held-out halves as R1 (s0A, s1A,
s1B, pooled), 95% cluster-bootstrap intervals, paired difference vs R1.
T-LLM counts as better than R1 if precision >= 0.80 AND F1 >= R1 F1 + 0.10
(R1: P 0.810, R 0.259, F1 0.392). Reported either way.

## Outcome (2026-10-12 19:37): auto-taxonomy NOT better than R1
Taxonomies from 493 history reviews: Zendesk 38, Freshdesk 23, Zoho 39, Help
Scout 12, LiveAgent 32, HappyFox 9 problems (one Zendesk chunk skipped: invalid
JSON 3x). Test classification: 143 coded, 162 "none", 33 "vague" (of 338).
| method | P [95%] | R | F1 [95%] |
| R1 | 0.810 [0.730,0.987] | 0.259 | 0.392 |
| T-LLM | 0.622 [0.527,0.931] | 0.214 | 0.319 | (ahead of R1 in 26% of resamples)
| T+R1 hybrid (approx.) | 0.660 [0.606,0.934] | 0.271 | 0.384 |
| T-emb (no LLM) | 0.492 [0.348,0.855] | 0.115 | 0.186 |
Rule (P >= 0.80 and F1 >= 0.492): FAILS. Contrast: the same LLMs grouping by the
TEAM codebook (built from these very reviews) reached F1 0.64-0.67, so that
earlier result depended on a taxonomy that already knew the test problems.
