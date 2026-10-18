# User-level judge v2 ("main problem"): pre-declared rule (written 2026-10-13, run 2026-10-14)

Background (user_level_rule.md, development half s0B, user-level key): R1 P 0.736 R 0.209 F1 0.325;
user-level judge P 0.567 R 0.438 F1 0.494 -> not adopted (P < 0.75). Recall doubled against every
key (Claude key 0.27 -> 0.53). Inspection of its mixed cases showed three error kinds:
(1) a case whose first complaint lists several problems pulls in complaints about the other ones
(macros case took "cannot submit a response", "cannot create ticket");
(2) neighbouring problems merged (sign-up and typing complaints joined "logged out repeatedly");
(3) label noise (e.g. a logout complaint labelled "dislikes new design").

One variant (U2), no further iteration on the development half:
the user-level prompt plus two instructions -
a) compare the MAIN problem of the new complaint with the MAIN problem of each case; a case's first
   complaint may mention several problems, only its main one defines the case;
b) problems in the same screen or area are still different problems when the user's experience
   differs, e.g. creating an account vs logging in vs staying logged in; using macros vs sending a
   reply vs creating a ticket.
Caveat recorded in advance: the examples in (b) come from errors seen on the development half, so
the development result is optimistic; only the one-shot confirmation counts.

Selection (development half s0B, user-level key, same stream and band as before):
P >= 0.75 AND F1 >= 0.375 (R1 0.325 + 0.05).
Confirmation (one shot, final halves s0A, s1A, s1B pooled): P >= 0.78 AND recall higher than R1
with the paired 95% interval (corrected cluster bootstrap) excluding 0.
Secondary (reported, not decisive): Claude and ChatGPT user-level keys and their agreed pairs;
case-level (B-cubed) precision; vague share.

## Outcome (2026-10-14 02:14) - U2 NOT ADOPTED (development bar not met; no further iteration)
Development s0B, user-level key: R1 0.736 / 0.209 / 0.325; v1 0.567 / 0.438 / 0.494; U2 0.671 / 0.422 / 0.518
(F1 bar 0.375 met, precision bar 0.75 not met). Case-level precision R1 0.93, v1 0.81, U2 0.84.
Secondary keys: Claude key U2 0.635 / 0.482 / 0.548 (R1 0.779 / 0.267 / 0.397); ChatGPT key U2 0.552 / 0.320 / 0.405.
The main-problem instructions recovered about half of v1's precision loss (0.567 -> 0.671) at a small recall cost.
