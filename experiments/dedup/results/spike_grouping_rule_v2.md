# Spike-level grouping v2: pre-declared rule (2026-10-09 14:05, before any v2 run)

Why v2: v1 (fixed tau 0.65, linked if ANY member pair is similar, connected
components) chained unrelated Firefox bugs into one 56-report group
(purity 0.80). v2 changes the two causes:

1. Threshold adapts to each product without labels: tau_p = the q-th percentile
   of all pairwise cosine similarities among that product's complaints in the
   evaluated stream (computable in production: no labels, no LLM).
2. Average linkage, no chaining: repeatedly join the two alert groups with the
   highest MEAN similarity over all their member pairs, while that mean >= tau_p.

Cases are never changed (RCA still sees them as they are); only alert counting.
Same embeddings and metrics as v1 (capture, capture on problems with >= 5
complaints, purity = B-cubed precision of alert groups, largest group).

Selection (on data already seen: Play Store within-company R1 halves s0A, s1A,
s1B, and Firefox sample 1 R1): q in {99.5, 99, 98.5, 98, 97, 96, 95}; pick the
q with the highest mean capture(>=5) over the two sets, subject to purity
>= 0.90 on BOTH. Ties -> the higher q.

Confirmation (one q, unchanged): Firefox sample 2 (data/external/firefox2.csv,
built from train.csv groups with no report or group shared with sample 1),
cases from a new R1 run. Secondary: Play Store unseen-company R1.

Pass: on Firefox sample 2, purity >= 0.90 AND capture(>=5) at least 0.05 above
cases-only. Otherwise v2 is rejected and reported as such.
