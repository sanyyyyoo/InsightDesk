# R1 integration plan

Goal: replace the app's cross-encoder dedup (F1 ≈ 0.02 on real reviews) with the
tested R1 pipeline, and add the spike path (detector v2 + group alerts), so the
app turns complaints into real problem cases, counts and alerts.

Everything below reproduces what was tested offline. Nothing is re-tuned.

## What R1 does (as tested)

For each new complaint, within its own product/company:

1. Clean text (boilerplate suppression) and embed (MiniLM, already in the app).
2. Find candidate cases: each case keeps **up to 5 diverse exemplar complaints**
   (a new member becomes an exemplar only if its cosine to every kept exemplar
   is < 0.85). A case scores by its best-matching exemplar.
3. Decide by the best score:
   - **≥ t_high (0.83)** → merge with the top case, no LLM call;
   - **< t_low (0.26)** → new case, no LLM call;
   - **in between** → LLM judge sees the new complaint plus the **first complaint**
     of each of the top 5 cases and answers `{"specific", "case"}` (the "gated"
     prompt).
4. Judge says not specific → **vague**: the complaint gets its own case and is
   never offered as a candidate later. Judge says case k → merge. Says 0 → new case.

Tested results: Play Store within-company P 0.82 (0.83 on the agreed subset),
Firefox P 0.92 / 0.96 / 0.96 on three fresh samples, never tuned on Firefox.

## Changes

### Phase A — R1 dedup (≈ 4–6 days)

| File | Change |
|---|---|
| `backend/services/dedup_r1.py` (new) | R1 logic: thresholds, exemplar retrieval, judge call, vague handling, the gated prompt copied word for word from the experiments |
| `backend/services/embedding_service.py` | store up to 5 exemplar vectors per case (`id = "<case_id>:<k>"`, metadata `case_id`, `product`); query with a `product` filter, top ~25, group by case (max score); `add_exemplar()` with the 0.85 diversity rule |
| `backend/services/duplicate_service.py` | call R1 instead of the cross-encoder when `DEDUP_MODE=r1` (default stays `cross_encoder` until the pilot switches it); keep the same return fields |
| `backend/llm/provider.py` | reuse `generate_json` (already temperature 0, `gpt-oss-120b` on Groq); add a timeout and one retry |
| config (`.env`) | `DEDUP_MODE`, `DEDUP_T_HIGH=0.83`, `DEDUP_T_LOW=0.26`, `DEDUP_TOP_K=5`, `DEDUP_REQUIRE_TOP1=false` |

Decisions built in:
- **Vague complaints** are not written to Pinecone at all, which is how "never a
  candidate" is enforced without a schema change.
- **LLM failure** (timeout, bad JSON, quota) → new case, never a guessed merge
  (precision first); logged so it can be re-checked.
- **Per product**: candidates only from the same `product`, as tested.
- Existing cases in Pinecone (one vector each) keep working: their single vector
  is treated as their first exemplar.

### Phase B — spike path (≈ 1–2 days; detector v2 is already done)

| Piece | Change |
|---|---|
| Detector v2 | done on branch `spike-detector-v2` (case alerts: ≥ 2 complaints, p < 0.001) |
| Alert groups | `backend/services/alert_groups.py` (new): per product, join cases whose complaints have mean similarity ≥ the product's 99th-percentile pairwise similarity (average linkage); run on the dashboard spike request or a periodic job |
| Group alerts | detector v2 with ≥ 3 complaints, p < 0.001, only for groups that join ≥ 2 cases; `/dashboard/spikes` returns case alerts plus group alerts (listing the cases inside) |
| RCA | unchanged: always per case (clean input) |

Tested: case + group alerts caught 75 % of simulated outbreaks on fresh Firefox 3
with 1.1 false alerts per 100 windows; the old detector caught 0 %.

### Phase C — small product decisions (≈ 1–2 days)

- Dashboard: show vague complaints as a per-product "general dissatisfaction"
  count instead of many one-complaint cases (needs one `is_vague` column, or a
  metadata table; to agree with the team).
- Escalation emails only for cases with ≥ N reports or a spike (RCA cost and
  fewer wrong emails). Optional: require the agreement rule (P 0.86–0.87) for
  auto-escalation.

## Tests before any commit

1. Unit: thresholds, exemplar diversity rule, vague handling, LLM-failure path.
2. **Equivalence**: replay the Play Store held-out halves and Firefox 3 through
   the app's R1 code with the cached judge answers → must reproduce the
   experiment assignments exactly (0 mismatches), as done for detector v2.
3. Local end-to-end (`test_e2e_local.py`, in-memory Supabase/Pinecone): ingestion
   → cases → spikes (case + group) → dashboard → RCA.
4. Real test project (option 1: a test Supabase project and a separate Pinecone
   index): same scenario on real services.
5. Usefulness review: replay the 1,432 real complaints; the team checks the top
   20 cases and their RCAs (correct / mixed / useless).

## Order and time

| Step | Time |
|---|---|
| A. R1 dedup + equivalence test | 4–6 days |
| B. Alert groups + group alerts | 1–2 days |
| Local end-to-end + real test project | 1 day |
| C. Vague bucket, escalation gating | 1–2 days |
| Replay of real data + team usefulness review | 1–2 days |
| **Pilot-ready** | **≈ 2½–3 weeks** |

Commits: on the fork (`sanyyyyoo/InsightDesk`), new branches, the `create_case`
bug fix as its own commit; pushed only after you approve.

## Not in scope now

- Unseen-company precision (0.68–0.75): future work; the onboarding/calibration
  mode is the practical answer for new companies.
- A better vague gate (our judge flags 26 % as vague vs 7–10 % for ChatGPT /
  Sonnet): pending the `gpt-oss-120b` labelling result, then a separate tested fix.
- Moving the judge to paid Groq / a local model: same code path; re-run the
  Play Store + Firefox checks if the model changes.

## Open questions for you

1. Pinecone: OK to change the index from 1 vector per case to up to 5 (same
   index, new ids)? The live index would need a one-time backfill.
2. Is `product` always filled on incoming complaints? R1 needs it to stay
   within one company.
3. Vague bucket: add an `is_vague` column to `cases`, or keep it out of the
   database for now?
