# Vague counter, confirmation on new apps: pre-declared rule (2026-10-13, before any run on this data)

Background: vague_area_spike_rule.md (Play Store, Zendesk + Freshdesk) found that a per-product
vague counter detects 100% of 10-complaint vague outages (cases only: 0%) for +0.15 false alerts
per 100 six-hour windows, but was "not adopted" because its relative false-alert criterion
(<= 1.25 x cases-only) was mis-specified for a tiny base rate (0.20). That result stands as
recorded. This is a NEW rule with an absolute budget, tested on data not used so far for spikes.

Data: the 588 new help-desk app reviews (Intercom 179, Jira Cloud 200, ServiceNow Agent 209) with
R1's real app decisions (reports/new_apps/replay_assignments.csv: case_id, route = vague or not).
Each app is one stream. Protocol as spike_sim.py / vague_area_spike_sim.py: 120 six-hour windows,
each review in a random window, detector v2 (m 2, p 0.001) on every counter, seed 5,
300 trials per setting split evenly over the three apps.

Counters: C = cases only (deployed); C+V = cases + one vague counter per app.
Settings:
- null stream (no outbreak): false alerts per 100 windows;
- vague outage: n = 5, 10, 20 injected copies of the app's R1-vague reviews in windows b..b+1
  (b random in 60-110), each copy a new singleton case. Detected = alert in b..b+2 on a counter
  holding outbreak complaints.

Adopt the vague counter if, pooled over the three apps:
- vague outage n = 10: C+V detection >= 0.80, AND
- null stream: C+V false alerts <= 1.0 per 100 windows, AND the vague counter adds <= 0.5.
n = 5 and n = 20 are reported, not used for the decision. Nothing is tuned.
Area counters are not tested here (no area labels for these reviews yet).
