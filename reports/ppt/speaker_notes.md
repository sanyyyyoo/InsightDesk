# InsightDesk – Speaker Notes (draft)

How to use this: the **Say** part of each slide is written to be spoken (about 1–2 minutes per slide). The **If asked** parts are for questions; don't read them out unless asked. Numbers are taken from the paper (reports/paper/InsightDesk_paper.pdf); where the deck and the paper differ, these notes use the paper's figures.

Three things the panel asked for are answered throughout:
1. **Data is domain-specific, not company-specific.** This is said up front on slide 1 and again on slides 14 and 18.
2. **No black boxes.** Every module is explained internally on slides 10–13, and Appendix A has a one-line internals card for each.
3. **Why each threshold, and what it was calibrated on.** See slides 12, 15 and 16, and Appendix B.

---

## Slide 1 – Title

**Say:**
"Good morning. We are Group 10: Krisha Sinnarkar, Sanyogita Shinde and Krushnam Sadrani, guided by Prof. Ganesh Wadmare. Our project is InsightDesk, a system that groups raw customer complaints into problem-level cases as they arrive, detects when a problem suddenly spikes, explains its likely cause, and escalates it to the right department after a person approves it. We are presenting the system and the paper we wrote on it.

Before we start, three points the panel raised last time.

**First, the data.** We were asked to keep the data domain-specific and not company-specific, and that is what we did. Our domain is customer-support and help-desk software. Our main data is public Google Play reviews of **six different help-desk products from six different companies**: Zendesk, Freshdesk, Help Scout, Zoho Desk, LiveAgent and HappyFox. We then tested on **three products we never tuned on**: Intercom, Jira Service Management and ServiceNow. We also ran a **leave-one-company-out** test, where thresholds tuned on the other companies were scored on the one left out. No single company's data drives any number we report. To show the method is domain-generic, we also tested it unchanged on two other kinds of text: **Mozilla Bugzilla bug reports** (Firefox, Thunderbird, and 233,000 reports including Eclipse) and **1,000 real IT service-desk tickets from Endava**.

**Second, credibility.** Every dataset's ground truth comes from a different source:
- Play Store: our own three annotators, working from a written codebook, agreeing at Fleiss' kappa 0.74.
- Bugzilla: duplicate links made by Mozilla's own triagers, completely independent of us.
- Unseen apps: two independent LLM labellers, treated only as secondary evidence.

**Third, no black boxes.** For every module we will show what goes in, what rule it applies, the exact threshold, and what data that threshold was calibrated on."

**If asked "why not use Vision Helpdesk's data?":** "Vision Helpdesk's setting motivated the problem, but we deliberately used public data from many companies in the same domain. That way the results are about help-desk complaints in general, not about one company's customers, and anyone can reproduce them."

---

## Slide 2 – Table of contents

**Say:**
"We'll go through the problem, the literature and where it falls short, our objectives, the architecture, how each module works internally with its formulas, the datasets and how we calibrated every threshold, the results against published methods, and then applications, future scope and conclusion."

---

## Slide 3 – Problem statement

**Say:**
"Help-desk platforms such as Zendesk, Freshdesk, Intercom and ServiceNow, and the companies that use them, receive complaints from app reviews, tickets, chat and web forms. One problem is reported many times in different words. For example, 'OTP never arrives', 'not getting the verification code' and 'can't log in, no SMS' are all one problem. Agents triage each one separately, and nobody sees that 40 customers are hit by the same issue.

Existing tools group by **theme**, such as 'login', rather than by **problem**, such as 'the OTP never arrives'. Keyword rules and topic models mix different problems that share words. A single similarity threshold has a dilemma: set it high and you miss paraphrases, set it low and you merge unrelated complaints. Feedback tools detect spikes with z-scores on whole categories, which miss a new problem growing from a low base.

So the need is a system that:
- groups complaints into problem-level cases **as they arrive**, with high precision;
- tracks each case's volume to catch incidents early;
- adds sentiment, topic and root cause;
- routes the incident to the responsible department after a human approves."

**Key line:** "Counting, alerting and escalation all depend on one step that most tools hide: deciding, for each new complaint, whether it is a problem we already know or a new one."

---

## Slides 4–6 – Literature survey (3 slides)

**Overall framing (say once at the start of slide 4):**
"We reviewed four families of work: app-review mining, duplicate bug-report detection, LLM-based matching and clustering, and incident or feedback analytics. For each paper the table shows its method, its parameters, its limitation, and what we do differently. For the classic methods we did not just cite them: **we re-implemented CLAP, BM25/REP, the SBERT threshold, BERTopic, MinHash and SimHash and ran them on our exact data with the same scoring**. So the limitations in the table are measured on our data, not only claimed. For the newer LLM papers, the numbers are the ones those papers report on their own data."

### Slide 4 – Literature survey (1/3): classic grouping methods

**CLAP (ICSE 2016) [1]**
- **How it works:** CLAP turns each app review into textual features and clusters them with DBSCAN. DBSCAN joins reviews whose distance is below eps, which is 0.6 in the paper. The goal is release planning: which bug-report groups to fix next.
- **What we found:** we ran it at the published eps 0.6 and at eps 0.75, tuned on our data. At the published setting precision is 0.84, but it finds only 2% of duplicate pairs. At its best setting F1 is 0.24.
- **Limitation:** it is batch-only, so it re-clusters everything each time and can't keep a stable case with a count. It groups by shared words, so 'login fails after update' and 'login is slow' land together.
- **Our improvement:** cases are formed online, and an LLM judge separates look-alike problems.

**REP / BM25F (ASE 2011) [2]**
- **How it works:** REP is the classic duplicate bug-report retriever. BM25F scores keyword overlap, weighted by term rarity, with k1 = 1.2 for term-frequency saturation and b = 0.75 for length normalisation. It adds metadata fields and returns the top-k likely duplicates.
- **What we found:** a recent TOSEM study found it still competitive with deep models. On our 233,521-report benchmark its top-5 hit rate is 0.43–0.44, against 0.46–0.56 for our retrieval.
- **Limitation:** it misses paraphrases with no shared words, such as 'can't sign in' and 'authentication keeps rejecting me'. It is also a ranking, not a decision.
- **Our improvement:** semantic retrieval, then an LLM verifies the match.

**Sentence-BERT (EMNLP 2019) [3]**
- **How it works:** Sentence-BERT is a bi-encoder. Each text becomes a vector independently, and similarity is the cosine between vectors. That is fast and indexable. The usual practice is one cosine threshold: above it is 'same', below it is 'different'.
- **What we found:** on our data no single cut is both safe and inclusive. The best F1 is about 0.10.
- **Our improvement:** two calibrated cuts (t_low and t_high) instead of one. The uncertain zone between them goes to the LLM judge.

**BERTopic (2022) [4]**
- **How it works:** BERTopic embeds documents, reduces them with UMAP, finds dense clusters with HDBSCAN, and labels each cluster with c-TF-IDF keywords.
- **What we found:** used as a grouping method, its precision on our data is only 0.16. One topic, such as 'login', holds many different problems. Several commercial feedback tools group this way.
- **Our improvement:** we still use BERTopic, but only to label already-formed cases with a theme and a department, never to form cases.

### Slide 5 – Literature survey (2/3): LLM-based methods

**Cupid (2023) [5]**
- **How it works:** ChatGPT first rewrites each bug report into its essentials, then REP retrieves duplicates. It reaches Recall-Rate@10 of 0.60–0.65, and the LLM is used on 40–60% of reports.
- **Limitation:** it still only ranks candidates. There are no cases, no counts, no spikes and no escalation.
- **Our improvement:** an actual join/new decision, which gives online cases that carry counts, spike alerts and RCA.

**Entity matching with LLMs (EDBT 2025) [6]**
- **How it works:** GPT-4 is used zero-shot as a pair judge ('do these two records refer to the same entity?'). It reaches F1 89.6–98.4 on record-matching benchmarks.
- **Limitation:** it judges every pair, so cost grows with the square of the data, and the cited LLM-as-judge surveys report position and verbosity biases.
- **Our improvement:** the judge is **bounded**. It is called only inside the calibrated band, sees at most 5 candidate cases, and makes **one decision per complaint**, never pairwise comparisons.

**GPTrace (ICSE 2026) [7]**
- **How it works:** LLM embeddings of crash reports, clustered with HDBSCAN over about 300K crashes.
- **Limitation:** batch clustering, and only for stack traces, which are very structured.
- **Our improvement:** online grouping of free-text human complaints.

**Dial-In LLM (EMNLP 2025) [8]**
- **How it works:** an LLM in the loop clusters customer-service call intents. It works on 100K calls, produces 1,507 clusters and reaches over 95% agreement with humans.
- **Limitation:** intents, such as 'wants a refund', are not problems, and it runs in batch.
- **Our improvement:** problem cases decided as each complaint arrives.

### Slide 6 – Literature survey (3/3): incident and feedback systems

**Lifecycle-aware clustering (AACL 2025) [9]**
- **How it works:** incremental clustering of support conversations, where an LLM splits clusters whose quality degrades (silhouette and Davies-Bouldin triggers).
- **Limitation:** it stops at clustering, with no spike detection, root cause or escalation.
- **Our improvement:** the full pipeline, with clusters feeding spikes, RCA and human approval.

**TickIt (FSE 2025, ByteDance) [10]**
- **How it works:** an LLM, fine-tuned on predefined ticket categories, escalates tickets.
- **Limitation:** a fixed category set means it cannot open a new problem nobody anticipated, and it has no spike detection.
- **Our improvement:** open-ended cases that can be created at any time, plus a CUSUM and the vague alarm.

**iPACK (ICSE 2023, Microsoft) [11]**
- **How it works:** it links customer tickets to cloud incidents using monitoring alerts, reaching F1 0.87–0.94.
- **Limitation:** it needs telemetry. Most SaaS support desks only have the customer's text.
- **Our improvement:** works from complaint text alone.

**SentiSum (commercial, 2025) [12]**
- **How it works:** anomaly detection per tag using a z-score above 2.
- **What we found:** we applied the same rule to our per-case counts. With 0–2 complaints per 6-hour window, the standard deviation is tiny or zero, so it detected **0%** of simulated outbreaks.
- **Our improvement:** a Poisson CUSUM detects 76–91% of outbreaks on bug-report streams.

**Close the literature section with the gaps:**
"Three gaps come out of this survey.
1. Existing work groups by topic, version or fixed category, not into problem cases decided online, so none can carry a stable count per problem.
2. Spike detection in feedback tools uses z-scores, which break at small counts, and nobody monitors the complaints the grouping can't place.
3. No published system we found combines online problem grouping of raw text, per-case spikes, cause explanation and human-approved escalation, and also reports labelled accuracy for the grouping step.

InsightDesk addresses all three."

**If asked "why compare against old papers like CLAP and REP?":** "They are still the standard baselines that recent papers compare against. The TOSEM 2023 study found REP still competitive. We ran them ourselves on identical data, so the comparison is fair. Newer LLM systems like Cupid and TickIt are compared on design, because their code or data isn't available for our setting."

---

## Slide 7 – Objectives

**Say:**
"Our five objectives, each mapping to one part of the pipeline:
1. Group duplicate complaints into problem cases **as they arrive**: similarity retrieval first, an LLM judge only for uncertain matches.
2. Measure sentiment with RoBERTa.
3. Find topics with BERTopic and use them to route cases to departments.
4. Detect spikes with a Poisson CUSUM, plus a separate alarm for surges of vague complaints.
5. Explain the root cause with an LLM, with **a human approving every escalation**."

---

## Slide 8 – Flow chart

**Say:**
"This is the path of one complaint. It is cleaned and embedded, then compared with existing cases. Depending on similarity, it joins a case automatically, opens a new case, or goes to the LLM judge. The judge can answer 'this case', 'none' or 'too vague'. Vague complaints go to an unassigned pool that has its own alarm. Every 6 hours, cases are re-joined and topics refreshed. Counts per 6-hour window feed the spike detector, and an eligible case gets a root-cause explanation that an operator approves before the email goes out."

---

## Slide 9 – System architecture & methodology

**Say (walk the colours left to right):**
"Nine phases in four stages.
- **Stage 1, intake and grouping (phases 1–4):** cleaning, embedding and retrieval, the decision band, and the LLM judge.
- **Stage 2, case upkeep (phases 5–6):** re-joining every 6 hours, then sentiment, topic and department.
- **Stage 3, incident signals (phases 7–8):** the Poisson CUSUM per case and per alert group, and the vague alarm per product.
- **Stage 4, action (phase 9):** the root-cause explanation and human-approved escalation.

**Storage:** cases, counts, windows and escalation history live in Supabase (PostgreSQL), and case vectors live in Pinecone. One important design point is that sentiment and topics are attached to cases for the dashboard and routing, but they **never affect grouping decisions**."

**Stack line, if time:** "FastAPI backend, React + TypeScript dashboard, MiniLM embeddings, Pinecone, gpt-oss-120b through Groq, Hugging Face RoBERTa, BERTopic."

---

## Slide 10 – Implementation (1/2): how grouping works internally

**Say (use the running example "Can't log in since the update, the OTP never arrives"):**

**Phase 1, intake and cleaning.**
"The customer submits through the React app. Cleaning is **label-free boilerplate removal**:
- The text is split into segments, such as sentences and clauses.
- A segment is boilerplate if it recurs in at least 8 complaints at cosine 0.90 or more, **and** the rest of those complaints is unrelated (mean cosine below 0.30). That catches 'Hi team, please help' without a hand-made list.
- We keep negations like *can't, never, not*, because 'works' and 'doesn't work' must not look the same.
- The original text is kept for display and for the judge."

**Phase 2, embedding and retrieval.**
"MiniLM converts the cleaned text into a 384-number vector of length 1, so the dot product equals cosine similarity.
- **Internally:** MiniLM is a 6-layer transformer distilled from a larger BERT-style model, then trained on about a billion sentence pairs so that paraphrases land close together.
- Each case stores up to **5 exemplars**: its founding complaint plus differently-worded members. A new member is stored only if it is less than 0.85 similar to every stored one, so each exemplar adds new wording.
- A case's score is its **best** exemplar match, not an average. An average of five different wordings matches none of them well.
- Pinecone returns the 60 nearest vectors, we rank them per case, and keep the top 5 cases. Our example's best case is 'OTP not received on login' at 0.71."

**Phase 3, decision band.**
- At or above 0.8306 it joins automatically.
- Below t_low it opens a new case: t_low is 0.40 for app reviews and chat, 0.26 for tickets.
- 0.71 is in between, so the judge decides.

**Phase 4, LLM judge.**
"The judge is gpt-oss-120b, an open-weight model. It sees the complaint and the **founding text** of up to 5 candidate cases. The prompt has a gate. It is told: *same problem means same feature AND same concrete symptom, so that one fix would solve both; same general area, like both about login, is NOT enough*. It first says whether the complaint is specific. It answers in JSON with the case number, 0 for none, or a not-specific flag.
- Temperature 0 and every answer is cached, so a replay gives identical decisions.
- An error or malformed answer opens a **new** case; a failure never merges.
- In our example, 'OTP never arrives' has the same symptom, so it joins (count +1). 'Login is slow' would open a new case."

**Same-user rule:** "If the same customer repeats the complaint within 24 hours, it is attached but not counted again, so one person can't inflate a case or trigger a spike."

**If asked "isn't the LLM a black box?":** "We don't trust it blindly, we bound it.
- Retrieval decides which 5 cases it may choose from.
- Thresholds settle the clear cases without it.
- It answers in a fixed JSON schema against a written rule.
- Failure never merges, and humans approve every escalation.
- Every decision is cached and auditable.

We measure the whole pipeline against human labels and Mozilla's own links, not against the LLM. And every cheaper replacement failed: a trained cross-encoder got precision 0.38, and small fine-tuned models 0.13–0.49."

**If asked about gpt-oss internals:** "It's a mixture-of-experts transformer: about 117 billion parameters in total, but only about 5 billion are active for each token, because a router picks a few expert sub-networks per layer. That's why it is fast and cheap: about 1.3 seconds and $0.24 per 1,000 judged complaints. It's open-weight, so a company can host it privately."

---

## Slide 11 – Implementation (2/2): upkeep, signals, action

**Phase 5, re-joining every 6 h.**
"Online decisions sometimes split one problem, because the first two reports looked different. Every 6 hours, for each case we take its 3 nearest same-product cases with similarity at least t_low. A case-pair judge sees up to 3 complaints from each side. The smaller case is absorbed: counts are summed and complaints, windows and vectors are moved. Each case takes part in **at most one merge per pass**, so a wrong decision can't cascade. Merges are 91–94% correct on bug reports and 66% on short reviews. That's honest: short reviews give the judge little to go on."

**Phase 6, sentiment and topics:** these are covered in detail on slide 13.

**Phase 7, spikes.**
"Counts per case per 6-hour window. The Poisson CUSUM collects evidence that the count rose by one report per window above normal. For example, 5 OTP complaints in 6 hours against a usual 0.1 raises a spike. The worked example is on the next slide."

**Alert groups:** "Since a problem can still be split, similar cases of one product are also summed and tested together. The cases themselves stay separate.
- The grouping threshold is the 99th percentile of that product's pairwise similarities, with average linkage, so the threshold comes from the data itself with no labels.
- A group needs at least 3 complaints."

**Phase 8, vague alarm:** "About 1 in 5 reviews is too vague to place, like 'app not working'. During an outage those never join a case, so per-case detectors see nothing. We count them per product and alarm on a surge. To our knowledge no published system watches the complaints its grouping can't place."

**Phase 9, escalation:**
- **Eligibility:** a case is eligible when it is not vague and has 3 or more reports, or an active spike.
- **RCA:** the LLM writes JSON with cause, affected segment, action, severity, confidence and evidence. It is **restricted to the case's own complaints and spike history**, and it lists the complaints it used, so a reviewer can check every claim.
- **Approval:** the operator approves before the email goes to the department.

---

## Slide 12 – Mathematical formulation (the "no black box" slide)

Go line by line, saying what each symbol means.

**Retrieval:** "e(x) is the MiniLM vector, normalised. S(x, C) is the best dot product between the complaint and case C's exemplars. We keep the top 5 cases."

**Decision band:** join if S* ≥ t_high; open a new case if S* < t_low; otherwise the judge decides.

**t_high = 0.8306, how it was calculated:**
"On the **Play Store tuning half**, we take every same-product pair of reviews with its human label (same problem or not), sort the pairs by similarity, and walk down from the top. Prec(t) is the share of true duplicates among pairs above t. t_high is the **lowest** t where that share is still at least 97%. It is read straight off the data, which is why it isn't a round number. **Why 97%:** a wrong automatic merge can trigger a wrong escalation, so automatic joins must be almost always right."

**t_low, how it was calculated:**
"Take only the true duplicate pairs and find the 20th percentile of their similarities: 80% of real duplicates lie above it, so the judge can still see them. That gave 0.26. Then we tested raising it on short text, measuring each setting with live judge calls:
- At +0.09 precision rose to 0.87 with recall unchanged.
- At 0.40 precision was 0.883 and recall 0.284, against 0.810 and 0.259, and judge calls fell from 86% to 66%.

We confirmed 0.40 on **unseen apps** under a pass rule written before running. On long bug reports it changed nothing, because their similarities are mostly above 0.40, so 0.26 stays for tickets and bug reports."

**Spike CUSUM, worked example:**
- The usual rate is λ = (complaints in the last 28 windows + 0.5) / (windows + 7). The 0.5 and 7 are a small prior, so a brand-new case starts at about 0.07 per window instead of zero and one complaint doesn't fire.
- The reference value is k = 1/ln((λ+1)/λ). This is the standard Poisson CUSUM value for detecting a rise from λ to λ+1. With λ = 0.1, k = 1/ln 11 = 0.42.
- The score is updated as S = max(0, S + count − k). With 5 complaints, S = 0 + 5 − 0.42 = 4.58, which is ≥ 2, so it is a **spike**.
- With 2 complaints, S = 1.58, not yet. If 1 more arrives next window, S = 1.58 + 1 − 0.42 = 2.16, so it **alerts**. Evidence accumulates across windows, which is what a single-window test can't do.

**Vague alarm:** "v ≥ 2 vague complaints in a window **and** the chance of seeing that many, given the product's usual vague rate, is below 0.1%."

**If asked "why does CUSUM beat z-score?":** "A z-score divides by the standard deviation. At 0–2 complaints per window it's almost zero or exactly zero, so the score is unstable or undefined. The CUSUM uses the Poisson model of counts and adds evidence over windows."

---

## Slide 13 – Sentiment & topic clustering

**Sentiment, internals:**
- **Model:** cardiffnlp twitter-roberta-base-sentiment-latest, a 12-layer RoBERTa-base (about 125M parameters), pretrained on about 124M tweets and fine-tuned on the TweetEval sentiment benchmark. Its last layer gives 3 scores (negative, neutral, positive), and softmax turns them into probabilities. We show the label and its confidence.
- **Why a Twitter model:** reviews are short, informal and full of slang, like tweets.
- **When it runs:** it is computed once from the case's **founding complaint**, so later reports don't make the label flicker.

**How it was evaluated:** "On real Play Store reviews, using star ratings as labels (1–2 negative, 3 neutral, 4–5 positive):
- RoBERTa: accuracy 0.707, negative precision 0.81 and recall 0.85.
- DistilBERT: accuracy 0.713, but it is binary, so it can't say neutral, and it is less precise on negatives (0.77). That's why we chose RoBERTa.
- Sentiment is **not** used for alerts; alerts depend on volume only."

**Topics, internals, step by step:**
1. Each case text becomes a MiniLM vector.
2. **UMAP** builds a 12-nearest-neighbour graph and squeezes 384 dimensions down to 5 while keeping neighbours together.
3. **HDBSCAN** finds dense regions. A topic needs at least 3 cases (min cluster size 3), and isolated cases become outliers instead of being forced into a topic.
4. **c-TF-IDF** treats each topic as one big document and picks the 1–2-word phrases that are frequent in it but rare in other topics. Those are the topic keywords.

**Quality:** "On the test deployment, 306 cases formed 44 topics with 13% outliers. Coherence c_v is 0.49, against 0.38 for random word sets, so the topics are moderately coherent. The largest are login/sign-in, notifications, reinstalling and crashes after updates."

**Department routing:** "It isn't an LLM, it's a transparent rule table.
- There are five departments, each with trigger words. For example, Authentication has *login, password, otp, signin, verification, token*.
- A topic goes to the department matching most of its top-5 keywords. No match goes to General Support, and an operator can override.
- Honestly, this is our weakest step: only 19 of 44 topics matched a named department."

**Upkeep:** "Topics are re-clustered every 6 h if cases grew 20% or outliers exceed 15%. These are empirical operating defaults, not tuned values, and we say so in the paper."

**Note:** the slide says 319 cases → 49 topics, 11.9% outliers, but the paper says 306 → 44, 13%. Quote **one** set consistently; the paper's is the measured one used for coherence.

---

## Slide 14 – Test datasets & label credibility

**Say (this is the domain-not-company slide; take your time):**
"Every dataset's ground truth comes from a different source, so no single labelling choice drives the results."

**Play Store, 6 help-desk apps (338 labelled of 450): tuning and held-out scoring.**
- Three of us labelled the reviews against a **written codebook** that defines a problem by its user-visible symptom: 'cannot log in', not 'login'.
- On a 50-review overlap all three labelled, Fleiss' kappa is 0.74 (95% CI 0.63–0.84), which is 'substantial' agreement.
- External check: GPT, Claude and gpt-oss given the same codebook agree with our key at kappa 0.68–0.70, about as well as humans agree with each other. So the codebook is reproducible, not our personal opinion.
- Labels were **frozen before** any pipeline variant was scored.

**Bugzilla, Firefox and Thunderbird (437 + 452): transfer test.**
- Duplicate links were made by Mozilla's own triagers during normal work, before our project existed.
- They are fully independent of us. Some duplicates are never linked, so a correct merge can be scored as wrong. Our precision there is, if anything, an underestimate.

**BugHub, 233,521 reports (Firefox, Thunderbird, Eclipse):** the standard public benchmark for duplicate retrieval.

**Unseen apps, Intercom, Jira SM, ServiceNow (588 reviews):**
- Never used for tuning.
- Labels are the agreed key of 2 LLM labellers (kappa 0.38 between them, so only pairs both agreed on count). This is secondary evidence; a 50-review human check is pending.

**Endava, 1,000 IT tickets:** a third domain, where labels are categories, so it tests case purity only.

**Synthetic, 488 complaints:** only to check each component behaves as designed. **Never** a headline result.

**Protocol (say it, the panel will like it):** "Thresholds are tuned on one half of the problems and scored on the other half, over three different splits, pooled. Confidence intervals come from a cluster bootstrap, verified by simulation to give 92–99% coverage. Every change was compared against the current version under a pass rule written **before** the run, so we couldn't move the goalposts."

**If asked "your Play Store labels are your own, isn't that biased?":** "That's why we have Bugzilla, whose labels are completely independent, and the result holds there: precision 0.87–0.96 with the same upper threshold."

---

## Slide 15 – Threshold calibration & sensitivity

**Say:**
"This table shows that our thresholds are a robust operating point, not a lucky fit. All rows are on held-out Play Store halves with live judge calls, before re-joining."
- **Long-text setting, t_low 0.26:** precision 0.810, recall 0.259, with 86% of complaints going to the judge.
- **Raising t_low:** to about 0.30 nothing changes; to about 0.35 precision rises to 0.867. At **0.40**, the deployed short-text setting, precision is 0.883 and recall 0.284, F1 0.430, and only 66% are judged. **Higher precision, higher recall and a quarter fewer LLM calls at the same time.**
- **Lowering t_high by 0.08:** precision stays about 0.81, so t_high is not on a knife edge. Only lowering it by 0.13 drops precision to 0.72.
- **Confirmation on unseen apps:** precision 0.608 → 0.635, with the judged share falling from 94% to 77%. That passed the bar we wrote beforehand: at least a 10-point drop in judge calls, and recall loss within 0.03.
- **Bug reports:** almost no change (96% → 90% judged, below the 10-point bar), so we kept 0.26 for long text.

**Key message:** "One upper threshold for every channel, a per-channel lower threshold, and every value was decided by a rule written before we saw the test result."

**If asked "why the 97% and 20% targets?":** "They are policy choices.
- 97% says how safe an automatic join must be.
- 20% says how many true duplicates we accept losing before the judge even sees them.

The evidence that they are robust is transfer. The same t_high, unchanged, gives precision 0.87–0.96 on bug reports, case precision 0.92 on unseen apps and 0.89 on an unseen company."

---

## Slide 16 – Spike detector calibration

**Say:**
"Same idea for the spike detector. We simulated outbreaks by taking the **real** complaints of one problem and squeezing them into a short burst inside a 30-day stream of 6-hour windows. Then we measured detection and false alarms per 100 windows.

We swept h over {1, 1.5, 2, 3, 4} and δ over {0.5, 1, 2}. **h = 2 with δ = 1 is the knee**:
- h = 1.5 adds about 10 points of detection but **ten times** the false alarms (3.81 vs 0.38 on bug reports).
- h = 3 loses a third of detections.
- δ = 1 means 'one more report per window than usual', the smallest rise worth acting on at these volumes.

h = 2 was chosen on Play Store and a first Firefox sample, then confirmed **unchanged** on unseen Firefox and Thunderbird streams under a pre-declared rule.

Alternatives on the same data:
- EWMA reaches 86% but at about 9 times the false alarms (3.19).
- A per-window Poisson tail test reaches 71% at 1.20 false alarms, three times the CUSUM's.
- The z-score that feedback tools use detects 0%."

**If asked "are complaint counts really Poisson?":** "No, and we checked. On 17,236 real Firefox reports, variance is 1.6 to 2.4 times the mean (overdispersed). So we never trust the nominal Poisson probabilities; every false-alarm rate on this slide is **measured empirically**, not computed from the formula."

**If asked "why 6-hour windows?":** "Four windows a day, so an outbreak is caught within a working shift, while a single case still gets enough reports per window to be measurable. The baseline is 28 windows, which is one week, so it covers weekday and weekend patterns."

---

## Slide 17 – Results: grouping quality

**Say:**
"**How we score:** pairwise precision means 'of the pairs we put together, how many are truly the same problem'; recall means 'of all true duplicate pairs, how many we found'. Every method was tuned at its own best setting on the same data and scored on the same held-out halves.
- **Play Store:** InsightDesk precision 0.83, recall 0.35, **F1 0.49**. The best competitor gets 0.25: BERTopic 0.25, CLAP 0.24, BM25 0.24, MinHash 0.20, cross-encoder 0.14, SimHash 0.12, single embedding threshold 0.10.
- **Firefox, thresholds unchanged:** F1 0.78, against at most 0.54 for the others.
- **At equal precision (0.80):** we find 35% of duplicate pairs, while BM25, MinHash and SimHash find about 1%. That is the fairest comparison, because a wrong merge costs more than a missed one."

**If asked "recall 0.35 is low":** "On 21-word reviews, two reports of one problem often look no more alike than reports of different problems, and even our human annotators agree only at kappa 0.74. We chose precision deliberately, because a wrong merge inflates counts and can trigger a false escalation, while a missed duplicate just leaves two smaller cases. Re-joining raised recall from 0.28 to 0.35, and alert groups plus the vague alarm keep split incidents visible. On longer bug reports recall is 0.57–0.66."

**If asked "why not just let an LLM group everything at once?":** "We tested it. One LLM call grouping a whole batch gets about the same offline F1 (0.50), but shuffling the input order kept only 78–95% of its grouped pairs (99% for an identical rerun), and it has no memory of earlier batches. Cases that change with input order can't carry counts or spike history. LLMs labelling with our codebook score well (precision 0.83–0.87), but that codebook was written from the test reviews; when the LLM builds its own problem list from earlier reviews, precision drops to 0.62, below InsightDesk's 0.81 on the same halves."

---

## Slide 18 – Results: precision vs recall

**Say:**
"Each dot is a method at its best setting. Up means more precise, right means more found.
- Everyone else is either precise and finds almost nothing, like CLAP's published setting (0.84 precision, 2% recall), or finds more but is imprecise, like the cross-encoder (precision 0.08).
- InsightDesk is the only one in the top-right region. The arrow shows the short-text setting moving it up and right at the same time.
- BERTopic's precision of 0.16 shows how many unrelated complaints share a topic.

**Generalisation, domain not company:**
- 3 unseen apps: case precision 0.92.
- Unseen company (leave-one-company-out): 0.89.
- Without a product field: 0.90, against 0.91 with it, so the system doesn't depend on product metadata.
- Retrieval on 233K bug reports: top-5 hit 0.46–0.56 vs REP's 0.43–0.44."

**Honest note if asked:** "Pairwise precision on unseen apps is lower (0.61–0.64), because errors gather in a few large mixed cases. That's why every escalation needs approval, and why we recommend a short calibration on a new company's own complaints for counts trusted without review."

---

## Slide 19 – Results: incident detection

**Say:**
- **CUSUM:** on bug-report streams it detects 76% of outbreaks per case and 91% per alert group, at under 1 false alarm per 100 windows. On short reviews it is 42–43%, because one outbreak spreads over more cases.
- **z-score**, used by feedback tools: **0%** on the same counts.
- **Vague alarm:**
  - Per-case detectors catch **none** of the vague-only outages, the ones made only of 'app not working'.
  - With the alarm we catch **100%** of those with 10+ complaints and 52% of those with 5, over 300 simulations per size. It costs only about 0.15 extra false alerts per 100 windows.
  - The threshold p < 0.001 with at least 2 was chosen as the loosest setting keeping false alerts at or below 2 per 100 windows on both tuning sets.
- **End to end**, on Firefox with re-joining: **94% of injected incidents** became escalation-eligible within 12 hours, with zero false alarms on streams with no incident.
- **RCA:** two blind raters preferred our grounded RCA prompt over an alternative (12:0 and 17:2) and found fewer unsupported claims.

---

## Slide 20 – Applications

**Say:**
"The method is domain-generic: nothing in it is trained on one company. It needs complaint text and, optionally, a product name.
- **Customer-support analytics:** recurring issues counted automatically.
- **App monitoring:** crashes after a release show up as a spiking case.
- **Banking:** transaction-failure complaints.
- **E-commerce:** delivery and payment issues.
- **Help-desk automation:** a draft diagnosis for agents.
- **Real-time monitoring** of any complaint stream.

We demonstrated the transfer across app reviews, bug reports and IT tickets."

---

## Slide 21 – Future scope

**Say:**
- Docker packaging and cloud deployment on the GCP or Azure free tier.
- Hosting the open-weight LLM locally, so no complaint leaves the company.
- Removing personal details before any LLM call.
- Using operator corrections to calibrate each company automatically. This addresses our main limitation.
- Testing the judge across models.
- Per-user limits, multilingual complaints, and automatic Jira tickets for approved escalations.

---

## Slide 22 – Conclusion

**Say:**
"InsightDesk turns raw complaints into stable problem cases as they arrive.
- Retrieval narrows each complaint to 5 candidates, calibrated thresholds settle the clear ones, an LLM judge decides only the uncertain ones, and re-joining repairs splits.
- **Grouping:** precision 0.83 and F1 0.49 on human-labelled reviews, the highest of every method tested. The same upper threshold transfers to bug reports (F1 0.78), unseen apps and an unseen company.
- **Incidents:** a Poisson CUSUM and the vague alarm detect incidents the usual z-score misses.
- **Escalation:** a person approves every escalation."

---

## Slides 23–24 – References

**Say:** "These are our references, all cited in the slides and the paper. The paper has the full list of 29." Don't read them out.

## Slide 25 – Thank you

**Say:** "Thank you. We're happy to take questions, and we can show the live system: submitting a complaint, seeing it join a case, and a spike being raised."

---

# Appendix A – Module internals cards (for "how does X work inside?")

| Module | What goes in | What it does inside | What comes out |
|---|---|---|---|
| Cleaning | Raw text | Splits into segments; drops a segment that recurs in ≥ 8 complaints at cosine ≥ 0.90 when the rest is unrelated (< 0.30); keeps negations | Cleaned text plus the original |
| MiniLM (all-MiniLM-L6-v2) | Cleaned text | 6-layer distilled transformer, about 22M params; token vectors mean-pooled into one 384-d vector; trained contrastively on about 1B sentence pairs so paraphrases are close; L2-normalised; 21 ms on CPU | 384-d unit vector |
| Pinecone | Vector + product | Vector database doing approximate nearest-neighbour search; stores exemplars with case id, product and vague flag; returns 60 nearest vectors, ranked per case by best exemplar | Top 5 candidate cases with scores |
| Decision band | Best score S* | Two thresholds: ≥ 0.8306 auto-join; < t_low new case; in between, judge | Join / new / ask judge |
| LLM judge (gpt-oss-120b) | Complaint + founding text of ≤ 5 cases | Mixture-of-experts transformer (about 117B params, about 5B active per token). Gated prompt: same feature + same symptom; first decides "specific?"; JSON output; temperature 0; cached; failure means new case | Case number / none / too vague |
| Re-joining | Cases | Every 6 h: 3 nearest same-product cases with similarity ≥ t_low; pair judge sees 3 complaints per side; one merge per case per pass | Merged cases (absorbed one hidden, not deleted) |
| RoBERTa sentiment | Founding complaint | 12-layer RoBERTa-base pretrained on about 124M tweets, fine-tuned on TweetEval; 3 logits, then softmax | Label + confidence |
| BERTopic | Case texts | MiniLM vectors, then UMAP (12 neighbours, 5 dims), then HDBSCAN (min cluster 3), then c-TF-IDF keywords (1–2-grams) | Topic + keywords |
| Routing | Topic keywords | Rule table, 5 departments with trigger words; most matches among the top-5 keywords wins; else General Support; operator override | Department |
| Poisson CUSUM | Counts per 6-h window | λ = (last 28 + 0.5)/(n + 7); k = 1/ln((λ+1)/λ); S = max(0, S + c − k); alarm at S ≥ 2, then reset | Spike / no spike |
| Alert groups | Complaint vectors of one product | Average-linkage join while mean similarity ≥ the product's 99th-percentile pairwise similarity; group needs ≥ 3 complaints | Groups tested with the same CUSUM |
| Vague alarm | Vague counts per product | Poisson tail: v ≥ 2 and P(X ≥ v) < 0.001 | Product-level alarm |
| RCA | Case complaints + spike history | LLM restricted to that evidence; JSON with cause, segment, action, severity, confidence, evidence | Cause report for the operator |
| Escalation | Case | Eligible if not vague and (≥ 3 reports or active spike); a human approves, then the email goes to the topic's department | Email |

# Appendix B – Every threshold: value, why, calibrated on

| Parameter | Value | Why / how chosen | Calibrated or confirmed on |
|---|---|---|---|
| t_high | 0.8306 | Lowest similarity where tuning pairs are ≥ 97% true duplicates | Play Store tuning half; confirmed on Bugzilla, unseen apps, unseen company |
| t_low (long text) | 0.26 | 20th percentile of true-duplicate similarities (80% kept reachable) | Play Store tuning half |
| t_low (short text) | 0.40 | Raised after live tests: precision and recall up, judge calls −23% | Play Store held-out; confirmed on unseen apps (pre-declared rule); no gain on bug reports, so 0.26 kept there |
| Exemplars per case / diversity cut | 5 / 0.85 | Store only new wordings; best-of-exemplars matching | Design choice |
| Candidates to judge | 5 | Bounds the judge's choice and cost | Design choice |
| Same-user repeat | 24 h | One person can't inflate a case; a repeat after a day is a real signal | Policy |
| Re-join | 6 h, 3 neighbours, 3 complaints per side, 1 merge per pass | Keeps errors local | Measured: 91–94% merges correct (bugs), 66% (reviews) |
| Window / baseline | 6 h / 28 windows (7 days) | Within-shift detection; weekly pattern | Design choice |
| CUSUM prior | 0.5 / 7 | New case starts at about 0.07 per window, so a single complaint doesn't alarm | Design choice |
| CUSUM δ, h | 1, 2 | Knee of the grid h ∈ {1, 1.5, 2, 3, 4}, δ ∈ {0.5, 1, 2} | Play Store + Firefox sample; confirmed on unseen Firefox/Thunderbird streams |
| Alert groups | 99th percentile, min 3 | Label-free threshold per product | Fresh Firefox sample (75% vs 68% detection) |
| Vague alarm | v ≥ 2, p < 0.001 | Loosest of p ∈ {0.01, 0.001}, m ∈ {2, 3, 4} with ≤ 2 false/100 windows on both tuning sets | Confirmed on 588 unseen-app reviews |
| Escalation | ≥ 3 reports or spike, plus human | Smallest repeated signal; a fast rise escalates early | Policy; 94% eligible within 12 h end to end |
| Topic re-cluster | +20% cases or > 15% outliers | Empirical operating defaults, **not tuned** (say so honestly) | — |
| BERTopic | 12 neighbours, 5 dims, min cluster 3 | Suited to a corpus of a few hundred cases; a topic needs 3 cases | c_v 0.49 vs 0.38 random |

# Appendix C – Fix before presenting (found while writing these notes)

1. **Every slide's date shows "26/6/2023".** Change it to today's date or remove it.
2. **Slide 13 says "319 staging cases → 49 topics, 11.9% outliers"; the paper says 306 → 44, 13%.** Use one set when speaking. The paper's figures are the ones used for the coherence result.
3. **Slide 10 says Pinecone returns cases "of the same product".** True when a product is given; the product field is optional, and with no product it compares across all products (0.90 precision without the field vs 0.91 with it). Say this if the demo uses a blank product.
4. **Play Store "338 labelled of 450":** be ready to say why 112 labelled reviews were not used in scoring. Check the experiment notes before presenting; these notes don't state the reason.
