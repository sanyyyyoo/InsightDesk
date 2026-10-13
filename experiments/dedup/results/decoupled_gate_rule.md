# Decoupled vague gate: pre-declared rule (2026-10-13, before any run of it)

Problem: R1's gate marks 21-24% of reviews that people (and both frontier LLMs) code as a specific
problem as "vague" (Play Store 23.7%, new apps 21%). The gate is asked inside the match prompt
("not specific, or no case matches, or not sure -> 0"), so "not specific" doubles as an exit when the
match is uncertain. The same model labelling reviews without candidates flagged about 11%.

Change: two separate decisions for a complaint in the band.
1. Specificity, asked ONCE per complaint with NO candidates shown (prompt SPECIFIC in e5_three_way.py,
   same definition of specific as R1's gate). Not specific -> vague singleton, exactly as R1 does now.
2. Matching for specific complaints only: prompt MATCH = R1's gated prompt with the specificity
   paragraph removed and nothing else changed (same feature AND same concrete symptom; same area is
   not enough; unsure -> 0), founder view, as in R1 otherwise. (Corrected before any run: the older
   "strict" prompt still tells the judge to answer 0 for complaints without a concrete symptom,
   i.e. a hidden gate, so it is not used here. The no-gate run of filtered_input_rule.md uses
   "strict" and is therefore "R1 with a softer, in-prompt gate", reported as such.)
Everything else as R1 (band, exemplar retrieval, top-5, per product). Flag: e5 --pre-gate.

Selection (development half s0B): qualifies if P >= 0.75 AND F1 >= 0.615 (R1 dev 0.779 / 0.585).
Confirmation (one shot): Play Store final halves pooled P >= 0.78 AND recall higher than R1 with the
paired 95% interval (corrected cluster bootstrap) excluding 0; Firefox 3 P >= 0.90.
Also reported: share of human-specific reviews called vague by the new step (target well below 24%),
and the no-gate result (filtered_input_rule.md) as the other end of the range.
