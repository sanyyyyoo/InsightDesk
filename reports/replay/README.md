# Replay review files and raters

| File | Content | Rater / model |
|---|---|---|
| top20_case_review.xlsx | top 20 cases (16 synthetic), v1 RCA | - |
| top20_real_case_review.xlsx | top 20 real-review cases, v1 RCA | - |
| rca_rating_chatgpt.xlsx | rating of the v1 RCAs, 20 real cases | ChatGPT, GPT-6 (account 1) |
| rca_rating_claude.xlsx | same | Claude Sonnet 5.5 |
| rca_ab_chatgpt.xlsx | blind A/B v1 vs v2, same 20 cases | ChatGPT, GPT-6 (account 2) |
| rca_ab_claude.xlsx | same | Claude Sonnet 5.5 |
| next20_real_case_review_v1/v3.xlsx | real cases ranked 21-40, v1 and v3 RCA | - |
| rca_ab3_chatgpt.xlsx | blind A/B v1 vs v3, ranks 21-40 | ChatGPT, GPT-6 |
| rca_ab3_claude.xlsx | same | Claude Sonnet 5.5 |

Rules: rca_v2_rule.md (v2 not adopted), rca_v3_rule.md (v3 adopted, default RCA prompt).

## Overall scores (descriptive only)
| Rater | Scope | Score | Note |
|---|---|---|---|
| ChatGPT (GPT-6) | v1 RCAs, top 20 real cases | 5/10 | "overstates the cause, fixes beyond the complaints" |
| Claude Sonnet 5.5 | all rating sheets together | 7/10 | grouping good, no RCA wrong; ~1 in 5 states unsupported specifics (recent update, platform/component, feature gap as bug) |
| ChatGPT (GPT-6) | round 3 A/B, set A / set B | 7/10 / 8/10 (overall 7.5) | A and B were randomized PER CASE (A = v3 in 11 cases, v1 in 9), so the set scores mix versions and cannot be attributed to v1 or v3 |

Version differences are judged only from the per-case A/B ratings (rules rca_v2_rule.md, rca_v3_rule.md).
Suggested v4 idea from the Claude review: use the strongest clue in the complaints instead of restating the symptom.
