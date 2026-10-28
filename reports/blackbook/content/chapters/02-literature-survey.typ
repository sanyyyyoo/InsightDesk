= Literature Survey

== Introduction

Work relevant to InsightDesk falls into four families: mining of app reviews and detection of emerging issues; duplicate detection, including the recent use of large language models as judges; near-duplicate and semantic deduplication of text; and incident management and feedback analytics in industry. This chapter reviews each family, compares the closest works with their parameters and limitations, and identifies the gaps that InsightDesk addresses.

== App-Review Mining and Emerging-Issue Detection

Mining app reviews for software engineering is a mature field; a systematic literature review by Dąbrowski et al. surveys its tasks and methods @dabrowski2022analysing. MERIT @gao2022emerging tracks topics across app versions with an online joint sentiment-topic model and flags topics whose share rises in a new version, explaining them with extracted phrases. Earlier, CLAP @villarroel2016clap grouped reviews that report the same bug with DBSCAN density clustering over textual features, to support release planning.

These systems work per app version or per topic rather than per problem case. A topic such as "login" holds many different problems, and none of these systems decides, as each review arrives, which existing problem it belongs to. They therefore cannot keep a stable count per problem over time.

== Duplicate Detection and LLM Judges

Duplicate bug-report detection is the closest research task to problem-level grouping. A recent large study by Zhang et al. @zhang2023duplicate found that classic retrieval methods such as REP @sun2011rep, built on the BM25F keyword ranking function, remain competitive with deep-learning models. Cupid @zhang2023cupid improves REP by first letting ChatGPT extract the essential information of each report, reaching a Recall-Rate\@10 of 0.60–0.65. These methods produce a ranked list of likely duplicates for a person to check; they do not decide whether a new report joins an existing group.

Sentence encoders such as Sentence-BERT @reimers2019sbert produce embeddings that can be indexed and searched quickly, while cross-encoders built on BERT @devlin2019bert read two texts together and are more accurate but cannot be indexed. Large language models used zero-shot as matchers reach F1 of 76.4–98.4 on six entity-matching benchmarks @peeters2025entity, and LLM judges agree with human preferences on many tasks @zheng2023judging @gu2024survey. The same studies document position and verbosity biases of LLM judges, which argues for bounding each decision: InsightDesk lets an LLM decide only among a few retrieved candidates and only when calibrated similarity thresholds cannot settle the case.

== Near-Duplicate and Semantic Deduplication

SimHash @manku2007simhash and MinHash with locality-sensitive hashing @broder1997resemblance detect near-copies of documents at web scale, and SemDeDup @abbas2023semdedup removes pairs of embeddings that are closer than a small distance $epsilon$ from large training sets. Benchmarks of text embeddings show that no single embedding model leads on every clustering task @muennighoff2023mteb. These methods target copies and near-copies; two complaints that describe the same problem in different words are usually far apart under them.

== Incident Management and Feedback Analytics

In cloud operations, iPACK @ipack2023 links customer support tickets to incidents using cloud monitoring alerts and reaches F1 of 0.87–0.94, and TickIt @liu2025tickit groups and escalates tickets with an LLM fine-tuned on predefined ticket categories (F1 0.88). LLM-based root-cause recommendation for cloud incidents @ahmed2023recommending @chen2024rcacopilot grounds its explanations in telemetry such as logs and metrics, in the spirit of retrieval-augmented generation @lewis2020rag. These systems depend on telemetry or on a fixed set of categories that most customer-support desks do not have.

Commercial voice-of-customer tools such as SentiSum @sentisum2025 detect anomalies per tag or theme, typically with a z-score against a historical baseline, and do not publish their grouping method or its accuracy. Topic modelling with BERTopic @grootendorst2022bertopic, which embeds documents, reduces them with UMAP @mcinnes2018umap and clusters them with HDBSCAN @campello2013hdbscan, is the approach behind several of these tools.

== Comparative Survey

@tbl:lit-survey compares the closest works with InsightDesk, giving the parameters each work uses, its main limitation for problem-level complaint grouping, and how InsightDesk addresses it.

#figure(
  table(
    columns: (2.6cm, 2.8cm, 2.9cm, 2.9cm),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Work*], [*Parameters / method*], [*Limitation*], [*InsightDesk*]),
    [MERIT @gao2022emerging], [Topic share per app version], [Groups topics, not problems], [Problem-level cases],
    [CLAP @villarroel2016clap], [DBSCAN, eps 0.6], [Batch only; shared words merge different problems], [Online cases; LLM judge separates look-alike problems],
    [REP @sun2011rep, study @zhang2023duplicate], [BM25F retrieval, top-k], [Ranking only; misses paraphrases], [Semantic retrieval with a join/new decision],
    [Cupid @zhang2023cupid], [LLM summary + BM25F], [No grouping decision, no cases], [Calibrated band + LLM judge],
    [LLM entity matching @peeters2025entity], [Zero-shot prompt per pair], [Judges every pair; cost grows with pairs], [One judge call per complaint, at most 5 candidates],
    [SemDeDup @abbas2023semdedup], [$epsilon$ = 0.00095–0.03], [Near-copies only], [Paraphrase-level matching],
    [iPACK @ipack2023], [Ticket–alert linking], [Needs cloud alerts], [Raw complaint text only],
    [TickIt @liu2025tickit], [Predefined categories], [Cannot open new problems], [Open-ended problem cases],
    [RCACopilot @chen2024rcacopilot], [Telemetry + LLM], [Needs telemetry], [Root cause from complaints],
    [SentiSum @sentisum2025], [z-score per tag, about 100-day baseline], [Fails at 0–2 complaints per window], [Poisson CUSUM + alert groups],
  ),
  caption: [Comparative literature survey],
) <lit-survey>

== Research Gaps

The survey shows three gaps that shape InsightDesk:

+ *Grouping by problem, online.* Existing systems group complaints by topic, app version or predefined category, not into problem cases decided as complaints arrive, so they cannot carry a stable count per problem.
+ *Spike detection at small counts.* Spike detection in feedback tools runs on per-tag z-scores, which are unstable at the zero to two complaints per window that a single problem produces, and no published system monitors the complaints that its grouping cannot place.
+ *An end-to-end, evaluated pipeline.* No published system we found combines online problem-case grouping of raw complaint text with per-case spike detection, cause explanation and human-approved escalation, and also reports labelled accuracy for its grouping step.

== Summary

App-review mining and topic models group by theme, duplicate-detection methods rank candidates without deciding, near-duplicate methods miss paraphrases, and incident-management systems depend on telemetry or fixed categories. InsightDesk is designed to fill the gaps above: it decides online which problem each complaint belongs to, builds small-count incident signals on those problem cases, and evaluates the grouping against human and independent labels.
