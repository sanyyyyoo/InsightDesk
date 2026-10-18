# Sensitivity checks (written 2026-10-18, before running). Report-only: no setting is changed by this run.
A. Threshold grid: t_low in {0.26, 0.30, 0.35, 0.40} x t_high in {0.70, 0.75, 0.80, 0.8306}, R1 as deployed
   (exemplars, top-5, same product, cached judge answers), Play Store held-out halves s0A, s1B, s1A pooled.
   Reported: pairwise P, R, F1, share of complaints judged, judge decisions missing from the cache
   (a miss counts as "no merge", so cells with many misses understate recall and are flagged).
   All cells lie inside the deployed band, so most decisions are cached.
B. CUSUM grid on the simulated outbreak streams (Play Store and Firefox 3 + Thunderbird, 300 trials, seed 5):
   h in {1, 1.5, 2, 3, 4} x shift delta in {0.5, 1, 2}; detection and false alerts per 100 windows.
C. EWMA baseline on the same streams: Z_t = a c_t + (1 - a) Z_{t-1}, alert when c_t >= 2 and
   Z_t > lambda_t + L sqrt(a / (2 - a) lambda_t), lambda_t = the same smoothed baseline;
   a in {0.2, 0.3}, L in {2, 2.5, 3}. Compared with CUSUM h = 2, delta = 1 at matched false alerts.
Amendment (2026-10-19, before re-running A): the first grid used fixed 0.26/0.8306, but published runs calibrate t_low/t_high on each tuning half, so its 'deployed' cell did not reproduce (299 cache misses). Re-run: per half, grid = calibrated (t_low + {0, .04, .09, .14}) x (t_high - {0, .03, .08, .13}); the (0, 0) cell must reproduce P 0.810 R 0.259.
