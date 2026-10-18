# Spike-detection review checks: pre-declared (written 2026-10-19, before running)

Asked by an external review. Reported as they fall; no change to the deployed detector unless (D) says so.
A. Same simulated Play Store streams, trials and seed as spike_sim.py (R1 cases and R1 alert groups):
   - detector v2 as deployed (count >= 2 and Poisson tail p < 0.001, baseline L 28, prior a 0.5, b 7);
   - raw count rule: alert when count >= m (m = 2, 3, 4), no probability test;
   - Poisson CUSUM: in-control rate = the same smoothed baseline, shift of interest +1 report per window
     (k = (l1 - l0) / ln(l1 / l0), l1 = l0 + 1), S = max(0, S + c - k), alarm at S >= h, reset after alarm;
     h chosen from {1, 1.5, ..., 8} as the smallest whose false alerts per 100 windows <= v2's in the same run
     (matched false-alarm rate), and also reported at h = 4 (a common default).
   Reported: detection within 12 h and false alerts per 100 windows for each.
B. Overdispersion on REAL timestamps (the simulation's background is random by construction, so it cannot
   test this): Firefox full Bugzilla history (BugHub CSV), one stream per component, 6-hour windows over the
   last 730 days of the data. Variance-to-mean ratio per component (components with mean >= 0.05), median
   and IQR, and pooled ratio with a 95% bootstrap CI over components. Plus detector v2's alert rate per 100
   windows on these real streams (no injected outbreaks; real bursts may exist, so this is an upper bound on
   its false-alarm rate) and the nominal rate implied by p = 0.001.
C. Vague alarm: report its detection and false-alarm rate from vague_area_spike_results.txt with the number
   of simulated outages (no new run).
D. If the pooled variance-to-mean ratio exceeds 1.5 AND v2's real-stream alert rate exceeds 2 per 100 windows,
   a negative-binomial variant is flagged as required follow-up work (not changed in this run).
