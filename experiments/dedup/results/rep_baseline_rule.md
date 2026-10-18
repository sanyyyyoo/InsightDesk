# REP-style duplicate-detection baseline on the BugHub split: pre-declared rule (written 2026-10-18, before running)

Why: duplicate-bug-report detection is the published systems' own task, so it is the fairest head-to-head.
REP (Sun et al., ASE 2011) is the standard strong baseline that deep models rarely beat.

Method (REP-style, our implementation, named as such in the paper):
- Retrieval: BM25F over title and description as separate fields (k1 1.2, b 0.75 per field), title weight w_t.
- Re-ranking of the top 400 candidates: score = BM25F_unigram + a * BM25F_bigram + c * [same component]
  + v * [same version] + p / (1 + |priority difference|).
- Weights (w_t, a, c, v, p) chosen by grid search maximising RR@5 on up to 2,000 TRAINING-split queries;
  scored once on the test-split queries used for every other system (same queries, same RR@k code).
Data: Firefox, Thunderbird, Eclipse Platform (BugHub train/test split), all earlier reports as candidates.
Reported beside: InsightDesk retrieval (MiniLM, title + description) and plain BM25 from firefox_rrk.py.
Reading: no pass/fail for us; the result is reported whichever way it falls. If REP-style beats our
retrieval, the paper says so and positions InsightDesk's contribution as the case/verification layer.

Amendment 2026-10-18 (before any result was read): to give REP exactly the input InsightDesk retrieval gets
(title + description text only), the primary comparison is REP-style TEXT ONLY (stage-1 weights, no
component/version/priority). REP-style FULL with metadata is reported separately as its native setting.
