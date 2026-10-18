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

## Amendment (2026-10-14 15:10, before any run; reason: a flaw found while implementing)
Injected COPIES of real reviews would be near-identical to their originals (cosine >= 0.83), so R1
would auto-merge them without the judge and "count captured" would be inflated. Changed to the
spike-simulation design: no copies. In each stream every labelled review appears exactly once; for
each incident problem (a user-level problem with >= 5 reviews) its own reviews are placed 30% in
random earlier windows and 70% in windows b..b+1; all other reviews are spread at random. Several
incidents share one stream at non-overlapping times (b at least 6 windows apart), so dedup runs
once per stream: Zendesk and Freshdesk, 2 streams each (seeds 7 and 8); incidents = every problem
with >= 5 reviews in that product (fewer than 20 per product - recorded as a deviation).
Thresholds as deployed in the app (0.26 / 0.8306), not re-calibrated. False alarms: one null stream
per product (all reviews at random times), units with no incident complaints. RCA right-symptom check
is a second step (one RCA per incident on its largest case, rated blind), run after the counts.
Systems: R1 as deployed; R1 + RJ1 if time allows (re-joining applied once per window).

## Addendum 2026-10-16: Firefox 3 second-domain check (written before running)

Why: on Play Store, R1 + RJ1 passed escalation (75%) and false alarms but failed alerts (35%) and
count captured (31%); incidents split into a median 6 cases and 30% of their complaints were vague.
Question: is that a property of short app reviews or of the pipeline? Firefox 3 (437 Bugzilla
reports, independent duplicate links, 24 problems with >= 5 reports) is the second-domain check.
Setup: identical to the main test (same stream builder, 30 days of 6-h windows, deployed thresholds
T_HIGH 0.8306 / T_LOW 0.26 - not retuned, same detectors and escalation policy), one product stream
"Firefox", incident seeds 7 and 8 (up to 16 incidents each), null stream seed 99. Systems: R1 and
R1 + RJ1 (one pass, applied once to the whole stream - optimistic on timing, as in the Play Store run).
Bars: unchanged (alerted within 12 h >= 80%; escalation-eligible within 12 h >= 70%; largest case
>= 50% or alert group >= 70%; <= 1 false alarm per week).
Reading: pass/fail is reported per bar for each system. Passing on Firefox but not Play Store would
mean alerting is limited by complaint wording, not by the detector; failing on both would mean the
alerting design needs work. Play Store verdicts are unchanged whatever this shows.
