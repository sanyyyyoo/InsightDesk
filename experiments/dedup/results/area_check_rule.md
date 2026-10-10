# Area check as a merge guard: pre-declared rule (2026-10-09 22:25, before any run)

Why: 55 of R1's 63 wrong merged pairs (87%) on the final Play Store halves join
complaints from DIFFERENT codebook areas (e.g. Login with Notifications).
Vague reviews often still name an area (labellers used login_unspecified etc.).

Area predictor (no LLM, no test labels): MiniLM embedding of the complaint vs
the embeddings of the 65 codebook DEFINITIONS (example_rows not used); the
area is the area of the nearest definition. confidence margin = similarity
of the best area minus the best definition from any other area.
Areas "Not a problem" and "Other" are never used to block.

Guard: when R1 merges a complaint into an existing case, block the merge if
area(complaint) != area(case founder) AND both margins >= mu. A blocked
complaint becomes its own case (conservative: in the app it might instead
join another case; later decisions are not re-run, so this is evaluated on
R1's original merges only - the keyword-gate lesson).

Selection on the dev half (seed 0, half B, R1 assignments), mu in
{0.00, 0.02, 0.05, 0.10}: highest pairwise precision subject to keeping
>= 90% of the correct merged pairs. Ties -> larger mu.

Confirmation, one mu, on the final halves s0A, s1A, s1B (pooled pairs):
PASS if pairwise precision >= 0.85 AND recall >= 0.90 x R1's recall (0.261).
Reported either way, with blocked right vs blocked wrong merges.
Caveat stated in advance: the codebook was drafted from this review pool,
so the area definitions are not fully independent of the test texts.
