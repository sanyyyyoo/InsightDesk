# Case re-joining pass: pre-declared rule (2026-10-13, before any run)

Why: rejoin_ceiling.py showed R1 splits true problems into several cases, the sibling fragment is
among a fragment's 3 most similar cases 68-80% of the time (Jira 37%), and a perfect case-pair
judge would lift Play Store recall from about 0.25 to about 0.8. The most similar case is the same
problem only about a third of the time, so the decision is the hard part. The earlier LLM merge
pass compared only the two cases' FIRST complaints and did not help; this pass shows more evidence.

Method (runs after R1, on R1's frozen cases; R1 itself unchanged):
1. Cases = R1's final cases; cases started by a complaint the gate called vague are left out
   (attaching vague complaints was right only 6/12 times, vague_second_look_rule.md).
2. Case similarity = highest cosine between any two members (MiniLM), same product only.
   Candidate pairs: each case with its 3 most similar cases, similarity >= the half's t_low.
3. Judge (gpt-oss-120b, prompt REJOIN in rejoin.py) sees up to 3 complaints of each case (the first
   complaint + the next two in arrival order) and answers whether both cases report the same
   problem: same feature and same failure, so one fix solves both; same area alone is not enough;
   unsure -> no.
4. Pairs are processed from most to least similar; a "yes" merges the two cases unless either has
   already been merged in this pass (no chains within a pass).
Variants: RJ1 = one pass; RJ2 = a second pass on the merged cases (same rules).

Selection (development half s0B only; R1 dev P 0.779, R 0.468, F1 0.585): a variant qualifies if
P >= 0.75 AND F1 >= 0.615 (R1 + 0.03). If both qualify: higher F1. If neither: reported as tried.
Confirmation (one shot): Play Store final halves s0A, s1A, s1B pooled: P >= 0.78 AND recall higher
than R1 with the paired 95% interval (corrected cluster bootstrap) excluding 0; Firefox 3: P >= 0.90.
Also reported (not part of the decision): Jira blind run (agreed key) and Thunderbird (if its R1
run is complete), case-level P/R, judge calls, merges made and how many were correct.

## Outcome (2026-10-13 23:30) - RJ1 ADOPTED by the rule
Development s0B: RJ1 P 0.752 R 0.523 F1 0.617 (qualified); RJ2 0.711 / 0.523 / 0.603 (not).
Confirmation: Play Store final halves pooled R1 0.810 / 0.259 / 0.392 -> RJ1 0.799 / 0.327 / 0.464;
difference P -0.011 [-0.069,+0.033], R +0.068 [+0.027,+0.119], F1 +0.071 [+0.027,+0.123].
Firefox 3: 0.963 / 0.546 / 0.697 -> 0.961 / 0.657 / 0.780 (22 merges, 20 correct).
Secondary, not decisive: Jira blind run (agreed LLM key) 0.650 / 0.101 / 0.174 -> 0.500 / 0.124 / 0.199
(5 merges, 2 correct; small sample, precision drop reported). Thunderbird skipped (its R1 run incomplete).
Thunderbird (added 2026-10-14 after its R1 run completed; reported, not decisive): see rejoin_confirm_RJ1_with_thunderbird.txt
