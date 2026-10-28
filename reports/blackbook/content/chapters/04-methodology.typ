// Long tables may continue on the next page (header row repeats).
#show figure: set block(breakable: true)

= Methodology

== Introduction

This chapter describes each of the nine phases of InsightDesk: its input, the rule it applies with its parameters, and its output. The running example from Chapter 3, "Can't log in since the update, the OTP never arrives", is followed through every phase. @tbl:parameters at the end of the chapter lists every parameter, its value and how it was chosen.

== Phase 1: Intake and Cleaning

A signed-in customer submits a complaint through the web application or an API client. The FastAPI service stores it with its product (optional), the verified user identity taken from the login token, and the source channel, such as web form, app review or chat. Text longer than 5,000 characters is truncated, and text shorter than 10 characters, or empty after cleaning, is rejected with a clear message.

Cleaning uses *label-free boilerplate suppression*. The text is split into segments: a short lead-in phrase ending in a colon or dash, then sentences and lines. A segment is a boilerplate candidate when a near-copy of it (segment cosine similarity at least 0.90) occurs in at least 8 complaints. It is confirmed as boilerplate when the remaining text of those complaints is unrelated, with a mean pairwise cosine similarity of at most 0.30, as with greetings such as "Hi team, please help". A segment that repeats because many customers report the same symptom is kept, because the complaints that share it are about the same thing.

The boilerplate list is recomputed every six hours over the most recent stored complaints (at most 2,000). A segment of an arriving complaint that is a near-copy of a listed boilerplate segment is dropped, and at least one segment is always kept. On the Play Store reviews used in this project the rule finds no boilerplate, while on Bugzilla bug reports it removes mostly template lines such as "Steps to reproduce:" and "Reproducible: always". The remaining text is lower-cased and stripped of punctuation and stop words, while negations such as _not_, _never_ and _no_ are kept, because "works" and "doesn't work" must not look alike. The original text is kept for display and for the LLM judge. For the running example, only the complaint itself remains.

== Phase 2: Embedding and Case Retrieval

Let $x$ be a complaint and $e(x)$ the unit-length MiniLM @wang2020minilm embedding (384 dimensions, sentence-transformers model all-MiniLM-L6-v2) of its cleaned text. The similarity of two complaints is then the dot product of their embeddings:

$ s(x, y) = e(x) dot e(y) $ <similarity>

Each case $C$ keeps a set $E_C$ of at most five *exemplars*: its founding complaint and up to four later members worded differently from those already stored. A new member $m$ is added to $E_C$ only if it is not already represented:

$ max_(m' in E_C) s(m, m') < 0.85, quad abs(E_C) <= 5 $ <exemplar-rule>

The score of complaint $x$ against case $C$ is its best match among the exemplars and, when the complaint names a product, only cases of that product are considered:

$ S(x, C) = max_(m in E_C) s(x, m) $ <case-score>

Exemplars let one case match differently worded reports of the same problem. With a perfect judge over the shortlist, diverse exemplars raised the pairwise recall that retrieval allows on the Play Store held-out halves from 0.58 (founding complaint only) to 0.72. Each exemplar is stored in Pinecone with its case, product, vague flag and the text of the complaint that founded the case. One query returns the 60 nearest vectors, which are ranked per case by their best exemplar, and the five best cases $cal(C)_5(x)$ are kept. Their best score is written $S^* = S(x, C^*)$.

== Phase 3: Calibrated Decision Band

The best score decides whether similarity alone can settle the complaint:

$ d(x) = cases(
  "join" C^* & "if" S^* >= t_"high",
  J(x, cal(C)_5(x)) & "if" t_"low" <= S^* < t_"high",
  "new case" & "if" S^* < t_"low",
) $ <decision-band>

where $J$ is the LLM judge of Phase 4. Both thresholds are computed from labelled pairs of complaints within the same product. With $y_i$ the true problem of complaint $i$ and $s_(i j)$ the similarity of complaints $i$ and $j$, the precision of all pairs at or above a similarity $t$ is

$ "Prec"(t) = abs({(i, j) : s_(i j) >= t, y_i = y_j}) / abs({(i, j) : s_(i j) >= t}) $ <precision-at-t>

and the upper threshold is the lowest similarity at which automatic joins are still at least 97% correct:

$ t_"high" = min {t : "Prec"(t) >= 0.97} $ <t-high>

The lower threshold is the 20th percentile of the similarities of true duplicate pairs, so that 80% of true duplicates lie at or above the band's lower edge and can still reach the judge:

$ t_"low" = Q_(0.20)({s_(i j) : y_i = y_j}) $ <t-low>

Calibrated on all 338 labelled Play Store reviews, these rules give $t_"low"$ = 0.26 and $t_"high"$ = 0.8306. These are the values used in the deployed system and in every test on other data. Within the Play Store evaluation, each tuning half yields its own values ($t_"high"$ 0.70–0.77, $t_"low"$ 0.24–0.30), so no Play Store score uses thresholds that saw the scored reviews.

The 20th-percentile rule proved conservative on short text. Raising the lower threshold to 0.40 on app reviews improved precision and recall together while sending fewer complaints to the judge; the setting was confirmed on unseen apps under a rule written before the test, whereas on long bug reports it made no real difference (Chapter 7). The deployed system therefore uses a lower threshold per channel and one upper threshold for every channel:

$ t_"low"(x) = cases(
  0.40 & "if the channel of" x "is an app review or chat",
  0.26 & "otherwise (tickets, bug reports, web form)",
) $ <t-low-channel>

In the running example $S^*$ = 0.71 lies inside the band, so the judge decides.

== Phase 4: LLM Judge

Inside the band, an open-weight large language model, gpt-oss-120b @openai2025gptoss served through the Groq API, receives the complaint and the founding text of each candidate case. It answers which case reports the same specific problem, none of them, or that the complaint is too vague to tell. The prompt, shown in @lst:judge-prompt, contains a gate: two complaints are the same problem only if they share the same feature and the same concrete symptom, so that one fix would solve both; being about the same general area is not enough.

#figure(
  ```text
  You decide whether a new customer complaint reports the SAME specific problem
  as an existing case. Same problem = same feature AND same concrete symptom,
  so that one fix would solve both. Different wording does not matter. Same
  general area (e.g. both about login) is NOT enough.

  First decide if the new complaint is SPECIFIC: it names a concrete symptom,
  error or behaviour (e.g. "access token revoked", "macros won't apply",
  "crashes when opening settings"). It is NOT specific if it only says
  something like "can't login", "doesn't work", "bad app", "too slow".

  If it is not specific, or no case is the same specific problem, or you are
  not sure, answer case 0.

  New complaint:
  {new}

  Existing cases:
  {cases}

  Return JSON: {"specific": true or false, "case": <case number that is the
  same problem, or 0 if none>}
  ```,
  caption: [Prompt of the LLM judge (backend/services/dedup_r1.py)],
) <judge-prompt>

The judge runs at temperature 0 in JSON mode, and every decision is cached. A chosen case is joined and its count rises by one; "none" opens a new case; "too vague" places the complaint in the unassigned pool of its product, which Phase 8 watches. An API error, a timeout or a malformed answer opens a new case, so a failure never merges two complaints.

The judge never acts alone. Retrieval decides which cases it may choose from, the thresholds settle clear matches and clear non-matches without it, a failed or uncertain answer never merges, re-joining limits each case to one merge per pass, and no escalation leaves the system without human approval. In the running example, "the OTP never arrives" matches the symptom of "OTP not received on login", so the complaint joins that case. In the evaluation runs, the band covered 66% of short reviews at the deployed setting and 90–96% of bug reports, and a judge decision took 1.34 s at the median.

== Phase 5: Case Re-joining

Online decisions split some problems across several cases, for example when the first two reports of a problem looked different and later reports bridge them. Every six hours a scheduler inside the API runs a re-joining pass. For every case $A$ it considers its three nearest cases $B$ of the same product whose similarity reaches the lower threshold:

$ sigma(A, B) = max_(a in A, b in B) s(a, b) >= t_"low" $ <case-similarity>

Candidate pairs are examined in decreasing order of $sigma$. An LLM case-pair judge sees up to three complaints from each case and decides whether both cases describe one problem. Each case takes part in at most one merge per pass, which keeps a single wrong decision from cascading. On a merge, counts are summed and the complaints, six-hour windows and exemplar vectors of the absorbed case move to the kept case, which keeps its founding text; the absorbed case is hidden, not deleted, and is never offered to the judge again.

== Phase 6: Enrichment: Sentiment, Topics and Routing

=== Sentiment

Each case receives a sentiment label from RoBERTa @loureiro2022timelms (the cardiffnlp twitter-roberta-base-sentiment-latest model, fine-tuned on the TweetEval benchmark @barbieri2020tweeteval) with three classes, negative, neutral and positive, and its confidence. It is computed once from the case's founding complaint, so later reports do not change it. Sentiment is shown on the dashboard and used for sorting and filtering; it is not used for alerts.

=== Topics

Topics come from BERTopic @grootendorst2022bertopic over the case texts. The case embeddings are reduced with UMAP @mcinnes2018umap (12 neighbours, 5 components, cosine distance), clustered with HDBSCAN @campello2013hdbscan (minimum cluster size 3, minimum samples 1), and each topic is described by its top keywords from a class-based TF-IDF over one- and two-word phrases (minimum document frequency 2). A topic is a theme that can hold many cases, such as "login and sign-in". Topics are recomputed on the first run, when the number of cases has grown by 20%, when outliers exceed 15%, or at a scheduled refresh; the 20% and 15% triggers are operating defaults chosen empirically, not tuned.

=== Department routing

Departments come from a fixed rule table, not from a language model. Five departments, Engineering, Authentication, Payments, Customer Success and Platform, each have a list of trigger words; for Authentication these include _login_, _password_, _otp_, _signin_, _verification_ and _token_. A topic goes to the department whose list matches most of its five top keywords, a topic with no match goes to General Support, and an operator can override the department in the dashboard. In the running example the case is labelled negative and placed under an authentication topic.

== Phase 7: Spike Detection

Complaints are counted per case $u$ in six-hour windows $t$, written $c_(u,t)$, with zeros filled in for empty windows. A repeat complaint from the same user about the same case within 24 hours is attached to the case but not counted again, so one person cannot inflate a case or trigger a spike. The expected rate is a smoothed mean over the previous $L$ = 28 windows (seven days), where $n_(u,t)$ is the number of past windows available:

$ lambda_(u,t) = (sum_(tau = t - L)^(t - 1) c_(u,tau) + a) / (n_(u,t) + b), quad L = 28, a = 0.5, b = 7 $ <baseline-rate>

The prior $(a, b)$ keeps new and quiet cases from alerting on a single complaint: a brand-new case starts from an expected rate of $0.5 slash 7 approx 0.07$ complaints per window. A Poisson CUSUM @page1954cusum accumulates evidence that the count has risen by $delta$ = 1 report per window above that rate, and raises a spike when the score reaches $h$:

$ k_(u,t) = delta / ln((lambda_(u,t) + delta) slash lambda_(u,t)) $ <cusum-k>

$ S_(u,t) = max(0, S_(u,t-1) + c_(u,t) - k_(u,t)), quad "spike if" S_(u,t) >= h, quad delta = 1, h = 2 $ <cusum>

The score restarts at zero after each alarm. In the running example, a usual rate of 0.1 gives $k = 1 slash ln 11 approx 0.42$; five complaints in one window give $S = 5 - 0.42 = 4.58 >= 2$, a spike.

Because one problem can still be split across cases, related cases of the same product are also summed into *alert groups* and tested the same way, while the cases themselves stay separate. Two cases are related when the mean similarity of their complaints reaches the 99th percentile of all pairwise similarities among that product's complaints, a threshold set from the data without labels; groups are formed by average linkage, so one similar pair alone cannot chain unrelated cases together.

== Phase 8: Vague-Complaint Alarm

Vague complaints join no case, so no per-case detector can see them. During an outage many customers write only "the app is not working". These complaints are counted per product $p$ in the same windows, $v_(p,t)$, with a baseline $lambda_(p,t)$ computed as in @eqt:baseline-rate, and tested with a Poisson tail rule:

$ "alarm"(p, t) <==> v_(p,t) >= 2 and P(X >= v_(p,t)) < 0.001, quad X tilde "Poisson"(lambda_(p,t)) $ <vague-alarm>

The threshold was fixed before testing, for the per-window Poisson test that the vague alarm reuses. Among $p in {0.01, 0.001}$ and a minimum count $m in {2, 3, 4}$, the rule picked the setting with the highest detection whose false alerts stayed at or below 2 per 100 windows on both tuning sets: $m$ = 2 with $p < 0.001$. An alarm reports when the surge started and which specific cases were active in the same windows, as leads for the investigation.

== Phase 9: Escalation and Root-Cause Explanation

A case is eligible for escalation when it is not vague and has at least three counted reports or an active spike of the case or of its alert group:

$ "eligible"(C) <==> not "vague"(C) and (n_C >= 3 or "alert"(C) or "alert"("group"(C))) $ <eligible>

Otherwise the dashboard explains why the case is not eligible, for example "only 2 reports and no active spike". For an eligible case, on request, an LLM writes a grounded cause hypothesis as JSON with the fields probable cause, affected segment, recommended action, severity, confidence and the complaints used as evidence. The prompt restricts it to the main symptom that most complaints share, treats requests for missing features as feature requests rather than faults, and forbids any detail that no complaint states. An operator reviews the explanation in the dashboard; an email reaches the department of the case's topic only after the operator approves it, and each approved escalation is recorded.

== Parameters and How They Were Chosen

@tbl:parameters lists every parameter of the pipeline, its value, the reason for it and the data on which it was calibrated or confirmed.

#figure(
  table(
    columns: (3.2cm, 3.4cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Parameter*], [*Value*], [*Why / calibrated on*]),
    [$t_"high"$], [0.8306], [Lowest similarity where labelled pairs are at least 97% duplicates; all 338 Play Store reviews; confirmed on Bugzilla, unseen products and an unseen company],
    [$t_"low"$ (long text)], [0.26], [20th percentile of true-duplicate similarities (80% kept reachable)],
    [$t_"low"$ (short text)], [0.40], [Raised after live tests (precision and recall up, fewer judge calls); confirmed on unseen apps by a pre-declared rule; no gain on bug reports],
    [Exemplars per case], [5, diversity cut 0.85], [Store only new wordings; design choice],
    [Candidates per judge call], [5], [Bounds the judge's choice and cost; design choice],
    [Same-user repeat window], [24 hours], [One person cannot inflate a case; policy],
    [Re-joining], [Every 6 h; 3 neighbours; 3 complaints per side; 1 merge per pass], [Keeps errors local; measured 91–94% correct merges on bug reports, 66% on reviews],
    [Window / baseline], [6 h / 28 windows], [Detection within a working shift; weekly pattern; design choice],
    [CUSUM prior $(a, b)$], [0.5, 7], [New case starts near 0.07 per window, so one complaint does not alarm],
    [CUSUM $delta$, $h$], [1, 2], [Knee of the grid $h in {1, 1.5, 2, 3, 4}$, $delta in {0.5, 1, 2}$; chosen on Play Store and a Firefox sample, confirmed on unseen streams],
    [Alert groups], [99th percentile, average linkage], [Label-free threshold per product],
    [Vague alarm], [$v >= 2$, $p < 0.001$], [Pre-declared grid over $p$ and $m$; confirmed on 588 unseen-app reviews],
    [Escalation], [$>= 3$ reports or a spike, plus approval], [Smallest repeated signal; a fast rise escalates early; policy],
    [Topic re-clustering], [+20% cases or >15% outliers], [Operating defaults, not tuned],
    [BERTopic], [12 neighbours, 5 dims, min. cluster 3], [Suited to a corpus of a few hundred cases],
  ),
  caption: [Parameters of the pipeline and how they were chosen],
) <parameters>

== Summary

Phases 1–4 decide, for each arriving complaint, which problem case it belongs to, using calibrated similarity for clear cases and a bounded LLM judge for the rest. Phases 5–6 keep cases correct and labelled over time. Phases 7–8 turn case counts and vague complaints into small-count incident signals, and Phase 9 turns an eligible case into a grounded, human-approved escalation.
