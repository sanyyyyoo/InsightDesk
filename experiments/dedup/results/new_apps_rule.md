# New help-desk apps, LLM answer keys: pre-declared rule (2026-10-12, before any run)

Question: how does R1 do on help-desk apps it has never seen, with no human
codebook, judged by independent LLM answer keys?

Data: Google Play reviews (google-play-scraper, newest first, collected
2026-10-12) of three apps not among the six used so far:
Intercom Conversations (io.intercom.android), Jira Cloud by Atlassian
(com.atlassian.android.jira.core; Jira Service Management has no separate app),
ServiceNow Agent (com.servicenow.fulfiller).
Test set: reviews with 1-3 stars and >= 30 characters (complaints); all of
Intercom (179) and ServiceNow Agent (209), and a random 200 of Jira Cloud
(seed 7): 588 reviews. Real review dates are kept as arrival times.

R1 runs exactly as deployed (frozen band 0.26 / 0.8306, gated judge prompt,
gpt-oss-120b, per app), before any answer key exists.

Answer keys (made independently of R1; different vendors from R1's judge):
- ChatGPT (GPT-6) and Claude Sonnet 5.5, each in a new chat with memory off,
  get the same blind sheet (app + review text) and one prompt: build your own
  list of specific problems per app, then give every review one problem code,
  "vague" (no concrete symptom) or "other". Each LLM's codes define its key:
  same app + same code = duplicates; vague/other = not grouped.
- Key reliability: agreement between the two keys (pairwise kappa on
  same/different for all within-app pairs, and adjusted Rand index).
- Optional human spot check: ~50 reviews labelled by a team member.

Scoring: R1 pairwise P / R / F1 and case-level (B-cubed) against each key and
against the pairs where both keys agree; 95% cluster-bootstrap intervals.
Compared with the main-branch pipeline (MS-MARCO -2.21) on the same reviews.
Reported as measured; no setting is changed on this data.

## Addendum (2026-10-12, before any run): A/B test of R1 vs trained-model variants
All 588 reviews of the sheet (each app = its own product), same harness (per product, exemplar retrieval, top-5,
founder text, band calibrated on the scored Play Store reviews only), one component
swapped per variant:
  V0 R1 (gated LLM judge, MiniLM retrieval)       = the deployed design
  V1 cosine only (no judge)                        floor
  V2 ce_A judge, MiniLM retrieval                  trained model replaces the LLM
  V3 ce_B judge, MiniLM retrieval                  same, with Endava pairs
  V4 R1 (LLM judge) with bi_C retrieval            trained retriever inside R1
  V5 ce_B judge with bi_C retrieval                fully trained, no LLM
Plus the app replay of R1 (replay_real_data.py) on the same reviews as a check that
the harness matches the deployed app.
Scored only after the ChatGPT / Claude keys exist: pairwise P / R / F1 and case-level,
95% cluster-bootstrap intervals, paired differences vs V0. Nothing is tuned on Jira.
(Widened from Jira only to all 588 reviews at the user's request, before any variant ran.)

## Addendum 2 (2026-10-12, before any Jira-only run): separate blind Jira-only run
The 200 Jira Cloud reviews are also run ALONE, as one company, with every variant
(app replay of R1 + V0-V5), each with its own empty LLM cache (replay: REPLAY_CACHE;
harness: cache named jira_new), so no decision from the 588-review run is reused.
Calibration stays on the Play Store reviews; no Jira review is in any training data.
Scored against the same answer keys (Jira rows only).
