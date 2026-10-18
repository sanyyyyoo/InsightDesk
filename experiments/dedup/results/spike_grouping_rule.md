# Spike-level grouping: pre-declared rule (2026-10-09, written before any run)

Purpose: cases stay as they are for RCA; for spike alerting only, cases whose
members are very similar are counted together ("alert groups").

Method (no LLM, no labels at run time):
- within one product, two cases are linked when the highest cosine similarity
  between any member of one and any member of the other is >= tau
  (MiniLM, the same boilerplate-suppressed text the pipeline embeds);
- alert groups = connected components of the links.

Metrics on alert groups:
- capture: share of a real problem's complaints in its largest alert group
  (all problems with >= 2 complaints; also problems with >= 5);
- purity: B-cubed precision of alert groups (how much of a complainant's alert
  group is the same problem);
- also the largest alert group size, to catch chaining.

Selection (decided now, on Play Store within-company R1 halves s0A, s1A, s1B only):
tau from {0.50, 0.55, ..., 0.90}; pick the tau with the highest capture on
problems with >= 5 complaints subject to purity >= 0.90. Ties -> the higher tau.

Confirmation: that single tau, unchanged, on
1. Firefox R1 (never used for any choice) - the real test;
2. Play Store unseen-company R1 (same reviews as selection, different splits;
   reported as secondary, not independent).
No other tau is reported for the confirmation sets.
