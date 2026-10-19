# t_low = 0.40 confirmation (written 2026-10-19, before running)
Found on Play Store (sensitivity A3): t_low +0.14 kept recall, raised precision 0.81 -> 0.91 and cut judged share 86% -> 61%.
That was chosen among 4 settings on the same data, so it must be confirmed on data that played no part:
Firefox 3 and Thunderbird (Bugzilla links), thresholds as deployed (t_high 0.8306), t_low 0.26 (deployed) vs 0.40,
same judge (gpt-oss-120b), prompt, view and caches, live calls for any decision not cached.
ADOPT t_low = 0.40 if, pooled over the two datasets:
  (a) precision(0.40) >= precision(0.26) - 0.01;
  (b) recall(0.40) >= recall(0.26) - 0.03;
  (c) share of complaints judged falls by at least 10 points.
Otherwise keep 0.26 and report 0.40 as a Play Store-only observation.
