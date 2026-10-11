# RCA prompt v2: pre-declared test rule (2026-10-11, before any v2 RCA is generated)

Why: on the 20 real-review cases of the replay, two independent raters (ChatGPT,
Claude) found no useless RCA but mostly "partly" useful ones (18/20 and 11/20),
and unsupported claims in 17/20 and 7/20: causes stated as fact ("recent
update", "token handling bug") and actions beyond the complaints. ChatGPT's
overall score: 5/10.

RCA v2 (backend/services/rca_service.py, RCA_PROMPT_VERSION=v2; v1 stays the
default until this test passes). Changes, all in what the RCA model is given
and asked:
1. evidence = the case's first complaint in its ORIGINAL wording (v1 showed the
   cleaned, stop-word-stripped text) + up to 7 more complaints, numbered;
2. probable_cause written as a hypothesis ("Likely: ...") naming only what the
   complaints show, with the complaint numbers that support it;
3. recommended_action limited to investigating / fixing the reported symptoms;
   no new features unless the complaints ask for them; no platform, version,
   component or timing the complaints do not mention;
4. other problems mentioned in the complaints are listed separately
   ("Also reported (separate): ..."), not folded into the cause;
5. same JSON schema as v1 (the dashboard and database are unchanged).

Test: the same 20 cases (top20 real-only cases of the replay), RCA v2 generated
from the same cached replay. A blind A/B sheet shows each case's v1 and v2 RCA
as "RCA A" / "RCA B" in random order (key kept separately). The same two raters
(new chats, memory off) rate both RCAs with the rubric and pick the better one.

v2 is adopted if, for BOTH raters:
- unsupported claims: v2 flagged in at least 3 fewer cases than v1, AND
- usefulness: v2 has no more "no" ratings than v1, AND
- preference: v2 preferred in more cases than v1 (ties not counted).
Otherwise v1 stays and the result is reported.

Addendum (before any v2 RCA was rated): raters also give an overall score out of
10 for the A set and the B set. Reported next to ChatGPT's 5/10 for v1; it is
descriptive only and not part of the adoption rule above.
