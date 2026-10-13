# Firefox Recall-Rate@k on the full benchmark: pre-declared rule (2026-10-12, before any run)

Data: the duplicate-bug-report benchmark files (BugHub) for Mozilla Firefox; the same
protocol is applied unchanged to Thunderbird and Eclipse Platform (added 2026-10-12,
before their runs)
(labelling/mozilla_firefox.csv: 115,814 reports 1999-07 .. 2013-12;
train.csv / test.csv: time split at 2011-04-05).

Protocol (standard duplicate-bug-report retrieval evaluation):
- queries: every report in test.csv that has duplicate links to an EARLIER report;
- candidates: all reports created before the query (the full history, not a sample);
- buckets: duplicate groups from union-find over all train+test links; a report
  without links is its own bucket; a bucket's score = max over its earlier members;
- RR@k = share of queries whose true bucket is among the top-k buckets,
  k = 1, 5, 10, 20.
Text = title + description cleaned exactly as in build_firefox_dbrd.py (UA,
crash/log lines, URLs removed), cut to 1000 characters.

Methods (no training, no tuning on Firefox):
- MiniLM cosine on the cleaned text: the retrieval stage of R1 as deployed;
- BM25 (k1 1.2, b 0.75) on the same text: the classic lexical baseline;
- MiniLM on the title only (titles are what most DBRD baselines lean on).
Reported as measured. Published numbers are quoted only if they use this same
dataset and split; otherwise the comparison is described as indicative.
This measures RETRIEVAL (does the right group reach the top k), not R1's merge
decision; R1 sees the top 5 cases.
