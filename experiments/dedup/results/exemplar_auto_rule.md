# Exemplar fix (EXA): pre-declared rule (written 2026-10-19, before running)

Problem found in the staging usability test: a complaint about two problems ("availability switch went
away ... and no dark mode") joined the dark-mode case through the LLM judge, became one of its exemplars,
and then pulled an availability-switch complaint into the dark-mode case (bridging).
Variant EXA: a complaint becomes an exemplar of its case only if it joined automatically (similarity
>= t_high) or founded the case; complaints joined through the LLM judge become members only.
Everything else as deployed (R1 thresholds, same judge and prompt, cached answers, re-joining RJ1 one pass).
Data: Play Store held-out halves s0A, s1B, s1A pooled; Firefox 3 and Thunderbird (Play Store thresholds).
Systems compared: R1+RJ1 (deployed) vs EXA+RJ1.
ADOPT EXA if all hold:
  (a) Play Store pairwise precision of EXA+RJ1 >= R1+RJ1 - 0.01 (point estimate);
  (b) Firefox 3 + Thunderbird pooled precision of EXA+RJ1 >= R1+RJ1 - 0.01;
  (c) recall loss <= 0.03 absolute on Play Store and on the pooled Bugzilla data;
  (d) re-joining merges correct (same majority problem) share does not fall.
Otherwise keep R1+RJ1 and report EXA as tested. Results reported whichever way they fall.
