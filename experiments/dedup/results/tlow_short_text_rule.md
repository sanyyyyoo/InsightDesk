# t_low = 0.40 for short-text channels (written 2026-10-19, before running)
Background: on Play Store reviews t_low +0.14 kept recall, raised precision and cut judged share by 25 points, but that
was chosen on the same data; on long bug reports (tlow_confirm_rule.md) it changed little (6 points) and was not adopted.
Question: does it hold on UNSEEN short reviews? Data: the 588 unseen-app reviews (Intercom, Jira Service Management,
ServiceNow), which played no part in choosing 0.40. Thresholds as deployed (t_high 0.8306), t_low 0.26 vs 0.40, same
judge (gpt-oss-120b), prompt, view and cache, live calls for anything not cached. Scored pairwise within each app
against the agreed key of the two LLM labellers (secondary labels, kappa 0.38).
ADOPT t_low = 0.40 as the setting for short-text channels (app reviews, chat) if:
  (a) precision(0.40) >= precision(0.26) - 0.01;
  (b) recall(0.40) >= recall(0.26) - 0.03;
  (c) the share of complaints judged falls by at least 10 points.
Long-text channels (tickets, bug reports) keep 0.26 whatever this shows. Caveat recorded with any outcome: LLM-made labels.
