# End-to-end acceptance test: pre-declared rule (written 2026-10-13, run 2026-10-14)

Question: does InsightDesk do what it is made for? For a real problem that suddenly affects many
users, does the system (1) show it as a case with a realistic report count, (2) raise an alert in
time, (3) make it eligible for escalation, and (4) explain the right symptom - without too many
false alarms? Task-level numbers ("caught 8 of 10 incidents within 12 hours"), not pairwise scores.

Data: real labelled reviews, one stream per product, 30 days of 6-hour windows (as spike_sim.py),
each review in a random window. Primary: Play Store, Zendesk and Freshdesk (user-level labels,
labels/playstore_user_level_map.csv). Secondary: the three new help-desk apps (Claude user-level-like
key, sheetX), clearly marked as LLM-labelled.
Incidents: 20 per primary product stream (40 in all), seed 7: a true problem with >= 5 reviews is
chosen at random; copies of its real reviews are injected, 30% spread over the days before window b
and 70% in windows b..b+1 (b random in 60-110), as in the spike simulation.
Pipeline: as deployed for dedup (R1, app thresholds), run ONCE per product on the stream with
injected copies (a copy of a review is judged like a new complaint; cached answers reused);
spike detector v2 on cases (m 2), alert groups (m 3), unassigned counter (m 2); escalation policy
as in backend/services/escalation_policy.py; RCA prompt v3 on the largest case of each incident.
Systems: R1 (deployed); R1 + RJ1 re-joining if rejoin_rule.md adopts it; user-level U2 if
user_level_v2_rule.md adopts it. Each system scored on the same incidents.

Measures per incident:
- count captured: share of the incident's complaints in its largest case, and in its alert group;
  number of cases the incident is split over;
- alerted in time: any alert (case, group or unassigned counter) on a unit containing incident
  complaints within windows b..b+1 (12 hours);
- escalation-eligible in time: a non-vague case containing incident complaints is eligible
  (>= 3 reports or spiking) within b..b+1;
- RCA right symptom: the RCA's "Likely" main symptom matches the problem's user-level definition,
  judged blind by two raters (the user's ChatGPT and Claude accounts, then a human sample), on a
  sheet with RCA text + problem definition only.
False alarms: the same streams without injection (null run): alerts per product per week.

Acceptance (all must hold for R1-as-deployed to be called fit for purpose; same bars for the others):
- alerted within 12 h for >= 80% of incidents;
- escalation-eligible within 12 h for >= 70% of incidents;
- median count captured (largest case) >= 50%, or (alert group) >= 70%;
- RCA right symptom for >= 80% of rated incidents (both raters);
- false alarms <= 1 per product per week.
Results reported per measure, with the share of incidents and 95% Wilson intervals. Nothing tuned.
