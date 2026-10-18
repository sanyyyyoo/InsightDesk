# Poisson CUSUM confirmation: pre-declared rule (written 2026-10-19, before running)

Selection (seen data, spike_review_results.txt): Poisson CUSUM with the deployed smoothed baseline
(L 28, prior 0.5/7), shift +1 report per window, h = 2, reset after alarm, beat detector v2 on Play Store
and Firefox sample 2 (same or higher detection, 3-5x fewer false alerts). h = 2 was chosen on that data.
Confirmation on unseen streams: Firefox sample 3 and Thunderbird, same simulation as spike_sim.py
(300 trials, seed 5, R1 cases and R1 alert groups), settings frozen (h = 2).
ADOPT CUSUM (replace the per-case and alert-group test; vague alarm unchanged) if, pooled over the two
datasets, for BOTH R1 cases and R1 alert groups:
  (a) detection(CUSUM) >= detection(v2) - 0.03, and
  (b) false alerts per 100 windows (CUSUM) <= false alerts (v2).
Otherwise keep v2 and report CUSUM as a strong baseline.
