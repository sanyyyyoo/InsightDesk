# Correction of the cluster-bootstrap intervals (2026-10-13)

## Problem
The 95% intervals resample whole true problem groups (issues) with replacement. A group
drawn k times was counted as k copies whose members all pair with each other, so a pair
INSIDE a group got weight k^2 (about 2 in expectation) while a pair ACROSS two groups got
weight k_g * k_h (about 1). Correct same-problem pairs were over-weighted against wrong
merges, so resampled precision was biased upward. Symptom: for low-precision methods the
interval did not even contain the point estimate (e.g. new apps, ce_A judge: P 0.205 [0.22, 0.49]).
Point estimates were never affected (all weights = 1).

## Fix (ci_bootstrap.counts / ci_bootstrap.bcubed)
Each draw of a group is its own copy: pairs inside a group count once per copy (weight k),
pairs across groups count over all copies (k_g * k_h), pairs between two copies of the same
group are not counted. Both kinds then have expected weight 1. B-cubed uses the same rule.
With all weights 1 the counts are identical to the original (checked on 500 random cases,
and B-cubed against a brute-force count). Shared by ci_bootstrap.py, compare_1432_real.py,
endava_eval.py, taxonomy_test.py and new_apps_score.py; the old function is kept as counts_v1.

## Validation (ci_coverage_sim.py)
Simulated test sets shaped like the Play Store set; true value = pooled precision/recall over
4,000 test sets; coverage = share of 300 test sets whose 95% interval contains it.

| wrong-merge rate | true P | old interval: P / R coverage | corrected: P / R coverage |
|---|---|---|---|
| 10% | 0.812 | 69% / 98% | 96% / 94% |
| 30% | 0.617 | 37% / 98% | 99% / 93% |
| 60% | 0.495 | 21% / 99% | 99% / 92% |

The old intervals failed worst for the low-precision methods (the trained judges); the corrected
ones are close to the nominal 95% (slightly conservative for precision).

## Effect on reported results (results/ci_corrected/)
Point estimates unchanged. Intervals for precision move DOWN and widen:

| result | old interval | corrected interval |
|---|---|---|
| Play Store within company, R1 P 0.810 | [0.750, 0.981] | [0.633, 0.961] |
| same, share of resamples with P >= 0.85 | 77% | 38% |
| R1 + agreement rule P 0.895 | [0.827, 0.992] | [0.741, 0.982] |
| agreement minus R1, precision | +0.085 [-0.016, +0.149] | +0.085 [-0.023, +0.227] |
| agreement minus R1, F1 | (not recorded) | -0.069 [-0.144, -0.007] (significant loss) |
| Play Store unseen company, R1 P 0.589 | [0.540, 0.912] | [0.419, 0.821] |
| Firefox 1 / 2 / 3, R1 P 0.922 / 0.959 / 0.963 | >= 0.85 in 99-100% | [0.774,1.000] / [0.894,0.996] / [0.894,1.000]; >= 0.85 in 87% / 99.6% / 99.6% |
| 1,432 stream, R1 within product minus main branch | (not computed) | P +0.238 [+0.064, +0.453], F1 +0.104 [+0.036, +0.173]: significant |
| 1,432 stream, R1 no product filter minus main branch | "ahead in ~90%" | P +0.148 [-0.022, +0.340], F1 +0.070 [-0.001, +0.145]: ahead in 96-97%, not significant |
| auto-taxonomy, R1 P 0.810 | [0.750, 0.981] | [0.616, 0.971] (different resample stream) |

Conclusions that change: the Play Store precision is less certain than reported (0.85 is
reached in 38% of resamples, not 77%); the agreement rule's F1 loss is now significant.
Conclusions that hold: R1 beats the main-branch pipeline; Firefox precision >= 0.89;
trained judges far below R1; R1's precision is clearly above cosine-only and below the oracle.
Endava intervals are recomputed when its rerun finishes.
