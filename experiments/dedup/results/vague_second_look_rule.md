# Vague second look: pre-declared rule (2026-10-13, before any run)

Problem: R1's gate marks 23-34% of complaints vague; each becomes its own case, is never a
candidate and never counted. The gate is the largest single source of missed duplicates
(stage_attribution.py: 75 misses at the gate vs 57 "no match"). Frontier LLMs with the human
instructions call only 7-11% of human-specific reviews vague.

Change tested (lever 1; area counters = lever 4 are a separate rule): R1 is unchanged for
every complaint it judges specific. For a complaint the gate marks vague, ONE extra judge call
("second look", prompt SECOND_LOOK in e5_three_way.py) asks whether it most likely reports the
same problem as one of the SAME candidate cases (same feature and same kind of failure, not just
the same area; unsure -> 0) and which product area it names. If it names a case:
- the complaint joins that case as an ordinary MEMBER: never a founder, never an exemplar, so the
  judge prompts of other cases do not change. (Not exactly zero change: the merged complaint no
  longer forms its own singleton case, so a later complaint whose closest case was that singleton
  may be routed differently; the number of new main-judge calls this causes is reported.)
- otherwise it stays a vague singleton exactly as now.
Variants: VS = merge into the named case; VS1 = merge only if the named case is the cosine top-1
candidate (agreement guard). The area answer is stored for the lever-4 test; not scored here.

Selection (development half s0B only, the half used to select R1): a variant qualifies if
pairwise P >= 0.75 AND F1 >= R1 dev F1 + 0.02 (R1 dev: P 0.779, F1 0.585 -> F1 >= 0.605).
If both qualify, the higher F1; if neither, the change is reported as tried and not adopted
(no wording iteration on the test halves).
Confirmation (one shot, untouched halves s0A, s1A, s1B pooled; Firefox sample 3; new apps
agreed key): adopted if pooled Play Store P >= 0.78 AND recall higher than R1 with the paired
95% interval (corrected cluster bootstrap, ci_correction_note.md) excluding 0, AND Firefox 3
P >= 0.90. Also reported: complaints recovered from the vague pool, cases per true group
(fragmentation), contaminated cases (purity), case-level P/R.
