# IT-ticket sanity check: pre-declared rule (2026-10-11, before any run)

Data: huggingface.co/datasets/saketgarodia1/IT-service-topic-classification-data
(47.8k IT service-desk tickets, text already lower-cased / stop-word-stripped,
8 topic labels; source and licence not stated). Sample: 1,000 tickets from the
TEST split, random, seed 7, fixed before any run. One company (no product
filter). No dates in the data: tickets arrive in sample order, spread evenly
over 30 days (so spike results are NOT meaningful here and are not reported).

What is measured (descriptive; no pass/fail, no tuning on this data):
1. Error floor: share of merged ticket pairs (and of multi-ticket cases) whose
   tickets carry DIFFERENT topic labels. A cross-topic merge is almost surely
   wrong, so this is a LOWER bound on R1's error rate; same-topic merges are
   not counted as correct (topics are much coarser than problems).
2. Case-level: cases, multi-ticket cases, largest case, vague share, routes.
3. The same for the main-branch pipeline (MiniLM + MS-MARCO cross-encoder,
   threshold -2.21) on the same 1,000 tickets, in the same order.
4. Top-20 R1 cases exported for a correct / mixed / useless review (raters as
   for the Play Store sheet).
R1 runs exactly as in the app (frozen band 0.26 / 0.8306, gated judge prompt,
gpt-oss-120b, temperature 0, RCA prompt v3 for the review sheet).
