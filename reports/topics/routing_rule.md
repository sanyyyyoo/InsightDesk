# Department routing: pre-declared rule (2026-10-12, before any run)

Question: does routing by problem AREA beat the app's current routing
(BERTopic topic keywords -> department_service keyword rules)?

Reference department per review = fixed table below applied to the TEAM's code
(450 labelled Play Store reviews). The table is written now, before any run,
using the app's own department names (department_mapping.py):

| area / code | department |
|---|---|
| Login, Account | Authentication |
| Stability, Performance, Install, Notifications, Text & editing, Media, Chat & calls, Privacy | Engineering |
| Tickets, Macros & canned replies, Layout, Design, Features, Analytics | Product |
| support_no_response | Customer Success |
| billing_plan_complaint | Billing & Accounts |
| Not a problem, Other | General Support |

Methods (per company as the app runs it: Zendesk, Freshdesk; all 450 also shown):
A. current app: BERTopic Config 8 topic of the review -> assign_department on
   the topic's top keywords ("General" and outliers count as General Support);
B. area table on the area predicted WITHOUT an LLM: nearest codebook definition
   (MiniLM, as in area_check.py);
C. area table on the area from the gpt-oss-120b codebook labels already made
   (llm_labels_playstore.jsonl) - i.e. the LLM that already reads every complaint
   naming its area.
Metric: share of reviews whose routed department equals the reference.
B or C is called better if it beats A by >= 0.15 on BOTH companies.
Caveat stated now: the reference uses the same table as B and C, so this tests
how well each method finds the AREA; the table itself is a product decision.

## Outcome (2026-10-12)
| scope | A current | B area, no LLM | C area from gpt-oss |
| Zendesk (243) | 0.288 | 0.737 | 0.823 |
| Freshdesk (124) | 0.177 | 0.742 | 0.895 |
| all 450 | 0.224 | 0.733 | 0.844 |
B and C both beat A by >= 0.15 on both companies. Note: the current keyword
rules have no "Product" department, so the 156 Product-reference reviews can
never be routed right by A; on the other reviews A is 70/153 = 0.46 (Zendesk).
