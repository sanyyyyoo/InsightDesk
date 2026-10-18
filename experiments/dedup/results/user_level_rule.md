# User-level problem definition: pre-declared rule (2026-10-13, before any run)

Why: R1 defines a case from a developer's view ("same feature AND same concrete symptom") and its
gate treats "can't log in", "too slow" as not specific. Real users describe what they experience,
not causes, so R1 discards or splits exactly the complaints a product receives most. Evidence: the
gate drops 21-24% of reviews people code as specific; asked alone (decoupled_gate_rule.md) the model
still drops 24% - the definition, not the prompt layout, is the cause.

Answer key (fixed before any run): labels/playstore_user_level_map.csv - 65 fine codes mapped to 43
user-level problems from code definitions only, debatable choices decided by the user on 2026-10-13
(no_internet_false_error = own problem; the rest as drafted). Stream: data/external/playstore_user.csv,
364 reviews = the 338 scored before + 26 "unspecified" reviews now scored ("can't log in", "keeps
crashing", "doesn't work"); praise / not-a-problem / off-topic / general "missing features" excluded
as before. Re-scoring R1's existing output at this level gives P 0.828 R 0.176 F1 0.291 (fine level
0.810 / 0.259 / 0.392), i.e. the coarser key alone makes R1 look WORSE.

Change: judge prompt "user" (e5_three_way.py PROMPT_USER), otherwise exactly R1 (band, exemplar
retrieval, top-5, founder view, per product): same problem = the same thing the user cannot do or the
same visible failure; different causes / error texts / details of that experience are the same
problem; different experiences are different problems ("cannot log in" vs "keeps logging me out";
"notifications don't arrive" vs "too many"); a complaint is set aside (vague singleton) only if it
names no problem at all (praise, question, "useless app", a rating with no reason).

Baseline: R1 (gated prompt) run on the same 364-review stream, same halves (split by user-level
problem, seeds 0 and 1 as before), scored with the same key.
Selection (development half s0B): qualifies if P >= 0.75 AND F1 >= R1's F1 on that half + 0.05.
Confirmation (one shot, final halves s0A, s1A, s1B pooled): P >= 0.78 AND recall higher than R1 with
the paired 95% interval (corrected cluster bootstrap) excluding 0.
Also reported, not part of the decision: the same runs scored against the blind Claude and ChatGPT
user-level keys and their agreed pairs; fine-level purity of the new cases (how mixed they are for
RCA); vague share; Firefox 3 with the user-level prompt (bug-level labels, so a precision drop there is
expected and is reported as such, not hidden).
