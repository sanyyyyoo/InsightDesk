# RCA prompt v3: pre-declared test rule (2026-10-11, before any v3 RCA is generated)

v2 result (rca_v2_rule.md, same 20 cases, blind A/B, raters GPT-6 and Claude):
v2 far more useful (yes 6->19 and 9->15) and preferred (19/20 and 14/20) but
unsupported claims fell 9->5 (GPT-6) and only 7->5 (Claude, rule needed -3):
NOT adopted. What raters still flagged in v2:
  - side symptoms folded into the cause (cases 3, 11, 13)
  - missing-feature requests debugged as faults (case 20)
  - small invented details: impacts, causes stated as fact (cases 7, 15)

RCA v3 = v2 plus three rules (RCA_PROMPT_VERSION=v3):
1. probable_cause covers ONLY the symptom most complaints share; other symptoms
   go to "Also reported (separate): ..." even when they appear in the same
   complaints; cite only the complaints that report the main symptom.
2. If most complaints ask for something the product does not have, the cause
   is "Likely: feature request - ..." and the action is product/backlog work,
   not debugging.
3. No impact, consequence, device, component, version, update or date that no
   complaint states.

Confirmation on NEW cases (v3 is tuned on the 20 cases above, so it is not
judged on them): the next 20 largest cases made only of real reviews in the
same replay (ranks 21-40). For each: v1 and v3 RCA, blind A/B in random order
(key kept separately), rated by the same two raters (GPT-6; Claude, same model
as before), new chats.

v3 is adopted (becomes the default RCA prompt) if, for BOTH raters:
- unsupported claims: v3 flagged in at least 3 fewer cases than v1, AND
- usefulness: v3 has no more "no" ratings than v1, AND
- preference: v3 preferred in more cases than v1.
Otherwise v1 stays; v2/v3 remain available behind the switch.
Overall /10 scores per set: descriptive only.

## Outcome (2026-10-11): v3 ADOPTED as the default RCA prompt
Blind A/B, 20 new real cases (ranks 21-40), key rca_ab3_key.csv:
| rater | useful yes v1->v3 | "no" | unsupported v1->v3 | preferred v1 / v3 / same | rule |
| GPT-6 | 9 -> 12 | 0 -> 0 | 12 -> 9 (-3) | 2 / 17 / 1 | pass |
| Claude | 11 -> 16 | 0 -> 0 | 6 -> 2 (-4) | 0 / 12 / 8 | pass |
Still flagged in v3 (GPT-6): an update or a specific component inferred as the
cause in a few cases (1, 2, 16, 17, 18); Claude: cases 5 and 18.
