# Spike detector v2: pre-declared rule (2026-10-09 16:35, before any v2 run)

Why: the deployed detector (complaint_windows rows only for non-empty windows,
7 prior rows needed, std 0 -> no spike) detected 0% of simulated outbreaks, even
with perfect grouping; counting empty windows as 0 instead fires on single
complaints (28-204 false alerts per 100 windows).

Detector v2, per unit (case or alert group), 6-hour windows, empty windows = 0:
- baseline rate lambda = (s + 0.5) / (n + 7), where s = complaints in the unit's
  previous L = 28 windows (7 days) since its first complaint, n = how many of
  those windows exist (0 for a brand-new unit). The 0.5 / 7 prior means "about
  one complaint every two weeks" for a unit with no history, so a new problem
  is judged against a low rate instead of being invisible.
- alert in window t when count_t >= m AND P(Poisson(lambda) >= count_t) < p.

Selection (data already seen: Play Store within-company halves, Firefox sample 1),
counting by R1 cases, same simulation as spike_sim_rule.md (300 trials, seed 5):
m in {2, 3, 4}, p in {0.01, 0.001}; pick the setting with the highest mean
detection over the two sets subject to false alerts <= 2 per 100 windows on both.
Ties -> larger m, then smaller p.

Confirmation (Firefox sample 2, one setting, unchanged):
- detector works: detection with R1 cases >= 0.70 and false alerts <= 2 per 100
  windows;
- spike branch helps: detection(alert groups v2) >= detection(cases) + 0.05 with
  false alerts <= 1.25 x the cases' rate.
Both reported separately; true-problem counting reported as the ceiling.
No app code changes until the whole pipeline is tested locally.
