# Spike-detection simulation: pre-declared rule (2026-10-09 16:25, before any run)

Question: does counting alert groups (spike branch, v2 grouping q=99) catch
outbreaks better than counting cases (today's setup), without more false alerts?
No LLM calls: cases come from finished runs and stay fixed; only arrival times
are simulated (limitation: the judge is not re-run in the simulated order).

Detector: exactly the app's (backend/services/spike_detection.py): per unit,
6-hour windows; history = every window from the unit's first complaint up to
the previous window; needs >= 7 history windows; z = (current - mean) / std;
std = 0 -> z = 0; spike when z > 2.

Timeline: 120 windows (30 days). One trial:
- outbreak problem P: a random real problem with >= 5 complaints in the partition;
- 30% of P's complaints (rounded up) uniform over windows 0 .. b-1 (background);
  the other 70% in windows b and b+1 (a 12-hour burst); b uniform in [60, 110];
- every other complaint uniform over windows 0 .. 119.

Outcomes per trial and counting method:
- detected: some unit containing a complaint of P in that window alerts in
  windows b .. b+2;
- delay: windows from b to that first alert;
- false alerts: alerts in a window where the alerting unit holds no complaint of
  P, per 100 windows (all units).

Methods: R1 cases | R1 alert groups (v2, q=99) | true problems (perfect counting,
ceiling) | cosine-only cases (reference).
Sets: Play Store within-company R1 halves s0A, s1A, s1B; Firefox sample 1;
Firefox sample 2 when its run finishes. 300 trials per set, seed 5.

Spike branch is supported when, on Firefox sample 2 AND pooled Play Store:
detection(alert groups) >= detection(cases) + 0.05, and false alerts per 100
windows <= 1.25 x the cases' rate. Otherwise it is reported as not supported.
