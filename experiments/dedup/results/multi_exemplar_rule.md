# Experiment 1 - judge sees several case examples: pre-declared rule (2026-10-11, before any run)

Why: the judge compares a new complaint with only the FIRST complaint of each
candidate case. Oracle with the same retrieval reaches recall ~0.79 within
company, R1 0.26-0.29, so the judge (not retrieval) loses most matches; the
gate-wording test showed the losses sit at "no matching case".

Only change: what the judge sees per candidate case.
- ex3: the case's first complaint + up to 2 more of its stored diverse
  exemplars (insertion order, cosine < 0.85 to each other), shown as
  "Case n: <text 1> | <text 2> | <text 3>".
- ex5 (run ONLY if ex3 fails): first complaint + up to 4 exemplars.
Frozen: R1 "gated" prompt word for word, wide band, exemplar retrieval, top-5,
gpt-oss-120b, temperature 0. Earlier, different views that are NOT this one:
"founder + latest member" (drift) and "founder + best-matching exemplar"
(precision 0.71-0.74).

Dev half ONLY (Play Store seed 0 half B; R1 there P 0.779 R 0.468 F1 0.585).
Qualifies if dev P >= 0.76 and F1 >= 0.605. Highest dev F1 wins; ties -> higher P.

Confirmation ONCE of the selected view (same bars as the gate rule):
1. Play Store final halves s0A, s1A, s1B pooled (R1 P 0.810, F1 0.392):
   pass if P >= 0.79 AND F1 >= 0.42;
2. Firefox sample 3 (R1 P 0.963, F1 0.697): pass if P >= 0.90 AND F1 >= 0.697.
Adopt only if both pass; report bootstrap intervals with it.

## Outcome (2026-10-11 ~01:55)
- ex3 on dev: P 0.064, R 0.471, F1 0.112 -> fails. One Zendesk case absorbed 69
  complaints from 8+ problems: after one slightly-wrong merge, the case's DIVERSE
  exemplars showed the judge several different problems, so it matched almost
  anything (snowball / clustering conflict).
- ex5 NOT run: it shows even more diverse exemplars and would amplify the same
  failure; recorded here instead of spending the calls.
- No confirmation run. R1 (founder only) stays.
