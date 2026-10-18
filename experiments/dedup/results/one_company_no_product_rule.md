# One company, several products, product not given: pre-declared rule (2026-10-14, before any run)

Question (user): in deployment the data comes from ONE company, and complaints may or may not say which
product they are about. When the product is unknown R1 searches the company's whole stream. How
much does that cost?

Data: Mozilla as one company = Firefox sample 3 (437 reports) + the Thunderbird sample (452), merged
in time order (created_at). The two samples share no duplicate groups (0 common issue ids), so every
case that mixes Firefox and Thunderbird reports is a wrong merge by construction.

Runs (R1 exactly as deployed: band calibrated on Play Store only, exemplar retrieval, top-5, gated
judge; e5 --data mozilla_combined --calibrate-on playstore, all reports labelled with one company):
- NO product filter: one stream, product unknown.
- WITH product filter: R1's existing per-product runs (firefox3 and thunderbird, same settings),
  pooled - identical to filtering by product because each product is its own stream.
Also cosine-only and oracle on the combined stream for context.

Reported (an evaluation of a deployment condition, nothing adopted or tuned):
pairwise P / R / F1 with the corrected cluster bootstrap for both runs, the paired difference, the
number and share of cases mixing the two products, and the complaints in them.
Pre-declared reading: if precision drops by more than 0.05 or more than 5% of multi-report cases mix
products, the paper and the app state that a product (or area) field should be captured when a
company has several products; otherwise R1 is reported as usable without it.

## Outcome (2026-10-14 23:09)
889 reports, 140 duplicate groups. Product filter: P 0.908 [0.76,0.99] R 0.578 F1 0.706, 0 of 156 multi-report cases mix
products. No product filter: P 0.899 [0.75,0.99] R 0.567 F1 0.696, 1 of 157 cases mixes products (2 complaints).
Difference P -0.009 [-0.050,+0.024], R -0.011 [-0.040,+0.017]. Cosine only F1 0.061; oracle F1 0.970.
Reading (pre-declared): R1 is usable without a product field.
