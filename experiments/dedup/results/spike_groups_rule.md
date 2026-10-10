# Alert-group spikes: pre-declared rule (2026-10-09 20:45, before any run)

Why: counting alert groups (v2 grouping, q=99) with the case detector settings
caught more outbreaks on Firefox sample 2 (0.86 vs 0.75) but had 2.18 false
alerts per 100 windows vs a ceiling of 2.11 (1.25 x cases), a narrow fail.
Groups are bigger than cases, so they get their own stricter alert setting.

System tested ("cases + group alerts"), as it would run in the app:
- case alerts: detector v2 (m=2, p=0.001) on every case, unchanged;
- group alerts: detector v2 with (m_g, p_g) on every alert group that joins
  >= 2 cases (single-case groups would only repeat case alerts);
- an outbreak is detected if any case or group containing one of its complaints
  alerts in windows b..b+2; a false alert is any case or group alert in a
  window where that unit holds none of the outbreak's complaints.
Simulation as in spike_sim_rule.md (300 trials, seed 5).

Selection on data already seen (Play Store within-company halves, Firefox 1,
Firefox 2): m_g in {2, 3, 4, 5}, p_g in {0.001, 0.0001}. Keep settings where
false alerts(system) <= 1.25 x false alerts(cases only) on EVERY seen set; pick
the highest mean detection gain over cases only. Ties -> larger m_g, smaller p_g.

Confirmation on Firefox sample 3 (data/external/firefox3.csv: no report or
group shared with samples 1-2), cases from a new R1 run, one setting:
PASS if detection(system) >= detection(cases only) + 0.05 AND false alerts
(system) <= 1.25 x false alerts(cases only). Also reported: cases-only detector
v2 against its own bar (>= 0.70 detected, <= 2 false per 100 windows).
