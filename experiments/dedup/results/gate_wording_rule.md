# Vague-gate wording: pre-declared rule (2026-10-11, before any run)

Why: as dedup judge, gpt-oss-120b flags 26% of Play Store reviews as vague
(not specific), but the SAME model labelling with the team's codebook rules
calls only 11% of the human-specific reviews vague (ChatGPT 7%, Sonnet 10%).
The gate prompt is stricter than the codebook: it lists "can't login" AND
"too slow" as not specific, while the codebook has a specific code for slow
performance. 102 of R1's 124 vague-flagged cases had a real duplicate.

Only the "is it specific?" paragraph of the R1 gated prompt changes; the rest of
the prompt, the band, exemplar retrieval, top-5 and the model stay frozen.

Variants (wording in e5_three_way.py, PROMPT_GATED_CB1/CB2; more may be added
ONLY if both fail on the dev half, at most 4 variants in total, each written
down here before it is run):
- cb1: specific = names WHAT goes wrong (feature/action + what happens);
  not specific only when no symptom at all ("bad app", "doesn't work",
  "useless", praise, rating only).
- cb2: cb1 + the codebook's own boundary: a complaint maps to a vague code
  (login_unspecified, crash_unspecified, app_not_working_unspecified,
  not_a_problem, other) only when it gives no detail; "too slow", "keeps
  logging me out", "no notifications" are specific.

Iteration and selection on the dev half ONLY (Play Store seed 0 half B, the
half R1 was chosen on; R1 there: P 0.779, F1 0.585):
a variant qualifies if dev precision >= 0.76 and dev F1 >= 0.605 (+0.02).
Among qualifiers: highest dev F1; ties -> higher precision. If none qualifies
after 4 variants: the gate stays as is and this is reported.

Confirmation, ONCE, of the single selected variant:
1. Play Store final halves s0A, s1A, s1B (pooled pairs; R1: P 0.810, R 0.259,
   F1 0.392): pass if P >= 0.79 AND F1 >= 0.42.
2. Firefox sample 3 (never used to choose anything; R1: P 0.963, F1 0.697):
   pass if P >= 0.90 AND F1 >= 0.697.
Adopt only if both pass. Reported either way, with vague-flag rates.
Known overlap (as for R1's own selection): the seed-0 dev half shares reviews
with the seed-1 halves; Firefox 3 is the fully independent check.

## Dev results so far (seed 0 B) and variant 3 (added 2026-10-11 01:05, before running it)
- cb1: P 0.774 R 0.422 F1 0.546 -> does not qualify
- cb2: P 0.802 R 0.462 F1 0.586 -> does not qualify (F1 level with R1 0.585)
- Diagnosis (dev only): vague answers fell to ~5% of calls, but "no matching case"
  rose to ~63%, ~26 of them with a true match offered; many are multi-problem
  reviews whose MAIN problem matches a case.
- cb3 = cb2 gate + matching at the codebook's granularity: same problem = the
  same failure of the same feature, at the level a support team would file ONE
  ticket; if the new complaint mentions several problems, match on its MAIN one;
  different details or wording do not make it a different problem. Everything
  else unchanged. Same qualification bar (dev P >= 0.76, F1 >= 0.605).
- cb3: P 0.655 R 0.532 F1 0.587 -> does not qualify (precision below 0.76; 23 wrong merges)
- cb4 (added 01:15, before running; the last allowed variant) = cb2 + only the sentence
  "If the new complaint mentions several problems, match on its MAIN problem." added to
  the same-problem definition; cb3's broader "one ticket" definition is NOT used.
- cb4: P 0.755 R 0.502 F1 0.603 -> does not qualify (P < 0.76 and F1 < 0.605, both narrowly)

## Outcome (2026-10-11 01:28)
No variant qualified within the 4 allowed. Per this rule the gate stays as R1
("gated"); no confirmation run was made. All four variants and R1 sit at dev
F1 0.546-0.603: wording moves the judge along the precision/recall trade-off
(cb2 highest precision 0.802, cb3 highest recall 0.532) but does not lift it.
