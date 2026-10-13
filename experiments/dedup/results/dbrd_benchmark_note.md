# Which published numbers can our Recall-Rate@k be compared with? (checked 2026-10-13)

Our files (labelling/mozilla_firefox.csv + train/test, thunderbird/, eclipse_platform/) are exactly the
logpai BugHub/BugRepo release: Firefox 115,814 reports (train 92,651 / test 23,163), Thunderbird 32,551
(26,040 / 6,511), Eclipse Platform 85,156 (68,124 / 17,032); the README states a chronological 80/20
split. BugHub itself publishes no results table; no paper found reports RR@k on this exact split.

Closest published numbers (indicative only, NOT directly comparable):
- "A Comparative Study of Text Embedding Models for Semantic Text Similarity in Bug Reports"
  (arXiv 2308.09193): Firefox / Thunderbird / Eclipse from a "Defects dataset", different split
  (Firefox train 88,374 / test 27,440; Thunderbird 23,389 / 9,161), test = child reports, train =
  parent and unique reports. Recall@5 (%): Firefox TF-IDF 13, BERT(all-mpnet-base-v2) 35, ADA 28;
  Thunderbird TF-IDF 14, BERT 26, ADA 30; Eclipse BERT 35, ADA 35.
- Ours (firefox_rrk.py, bucket-level RR@5, all earlier reports as candidates): Firefox MiniLM 0.551,
  BM25 0.406, trained bi_C 0.593; Thunderbird 0.560 / 0.443 / 0.616; Eclipse 0.456 / 0.402 / 0.523.
Differences in split, candidate pool and bucket definition (we score the true duplicate GROUP, best
member) plausibly explain much of the gap, so the paper must not claim to beat 2308.09193; it can
report our numbers on the public BugHub split as a reproducible reference point, and our own BM25 /
MiniLM / trained-model comparison on the same split as the like-for-like comparison.
