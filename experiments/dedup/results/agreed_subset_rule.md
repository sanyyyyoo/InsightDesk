# High-agreement test subset: pre-declared rule (2026-10-10, before scoring)

Why: about a quarter of the reviews are read differently by different people
and models; scoring on them measures label ambiguity as much as the pipeline.

Label of a review: the team's final label, replaced by the blind 3-person
majority where the relabel round covered it (relabel_majority.csv).

A scored review is KEPT when its label is confirmed by at least one more
independent reader:
- relabel reviews: the majority had >= 2 of 3 humans (all of them);
- other reviews: ChatGPT (top model) OR Claude Sonnet 5.5 chose the same code.
Both LLMs labelled blind with the human sheet's exact rules.

Scoring: pairs among kept reviews only (excluded reviews are ignored, not
counted as errors either way). Same frozen runs, no re-running: R1, R1 +
agreement rule, cosine only, oracle; within company (s0A, s1A, s1B) and
unseen company (LOPO).

Status: SECONDARY result next to the full test set, never instead of it.
Caveat stated in advance: the subset is chosen partly by LLM agreement and
the pipeline's judge is an LLM, so the subset may favour reviews LLMs find
easy; the full-set numbers remain the headline.
