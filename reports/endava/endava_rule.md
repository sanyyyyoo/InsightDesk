# Endava help-desk tickets: pre-declared rule (2026-10-12, before any run)

Replaces the paused 8-topic IT-ticket check (same source data, finer labels).

Data: all_tickets.csv (Endava internal help-desk tickets, released by Microsoft
CSE, github.com/karolzak/support-tickets-classification; 48,549 tickets; text
already preprocessed by the publisher; dataset licence unspecified).
Sample: 1,000 tickets, random, seed 7, fixed before any run. Text = title + ". "
+ body (title empty for 1.5%). One company (no product filter). No dates in the
data: tickets arrive in sample order, spread over 30 days (spikes not reported).

Label: (category, sub_category1, sub_category2) as one code - the finest
operational category. It is a routing category, NOT a duplicate group, so:
- precision at this level = share of merged pairs with the same category code;
  1 - precision = cross-category merges = a LOWER BOUND on wrong merges;
- recall at this level measures how much same-category tickets are grouped, an
  upper-level view; it is reported but is not "missed duplicates".
Also reported excluding the single largest category (37% of all tickets),
where same-category merges say least.

Pipelines on the same 1,000 tickets, same order:
- R1 exactly as in the app (band 0.26 / 0.8306, gated judge, gpt-oss-120b);
- main branch: MiniLM top-5 + MS-MARCO cross-encoder, -2.21.
Metrics: pairwise precision / recall / F1 and case-level (B-cubed) with 95%
cluster-bootstrap intervals, paired difference R1 - main branch; cases,
multi-ticket cases, largest case. Descriptive: no tuning on this data.
Top-20 R1 cases exported for review (text only; labels are anonymous codes).
Note (2026-10-19): 1 ticket longer than the API's 5,000-character limit is truncated to its first 5,000 characters, as a customer would have to do.
