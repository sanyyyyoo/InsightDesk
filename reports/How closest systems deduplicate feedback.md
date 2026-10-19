# How the closest systems deduplicate feedback

This report asks how the systems closest to InsightDesk turn raw feedback into problem-level groups, and what InsightDesk can borrow from them. It covers 12 systems and records, for each one, what text it groups, the similarity measure, the algorithm, the threshold, how clusters are maintained over time, and how grouping was evaluated. It then maps the lessons onto our offline dedup experiments (branch `dedup-experiments`, results not pushed).

## 1. Summary

- **Only a few published systems group individual reports into "same problem" clusters and report their method.** These are CLAP, DoorDash, the Oracle 2026 support-chat system, and Hark (Google). IDEA, MERIT, DIVER and iFeedback detect emerging topics or keyword combinations, not report-level cases. SentiSum, Enterpret and Unwrap do not disclose their grouping methods.
- **InsightDesk's design (top-5 vector shortlist, then a verifier) has a direct published counterpart:** Oracle's 2026 incremental assignment. Oracle shortlists the top 5 clusters by cosine similarity and asks an LLM to confirm the match. In their ablation, LLM matching gave 36% better silhouette than cosine alone.
  - Our experiments showed the STS-B cross-encoder is a *weaker* verifier than plain MiniLM cosine (AUC 0.826 vs 0.918). The fix is a stronger verifier (an LLM or a fine-tuned model), not dropping the verification step.
- **Mature systems do not rely on online assignment alone.** Oracle runs periodic merge (with LLM review), split and prune steps; FeClustRE uses batch agglomerative clustering. This matches our result that batch clustering has much higher recall than online assignment. Held-out pairwise F1 was 0.774 for batch versus 0.612 for online cosine and 0.345 for v1.
- **The main thing they do that InsightDesk does not is normalise text before clustering.** Hark generates 2–4 word issue phrases, and Oracle, LLM-Cure and Chhetri et al. extract short concerns, features or aspects. Clustering then happens on the problem statement, not on the whole message with greetings and filler. This directly targets our biggest measured error source: shared stock phrases, whose removal cut contaminated cases from 18 to 6.
- **Almost none of them evaluate grouping against ground-truth duplicate labels with pairwise precision and recall.** CLAP uses MoJoFM, Oracle and FeClustRE use silhouette and Davies–Bouldin (intrinsic scores, no labels), and DoorDash reports a business metric. InsightDesk's pairwise P/R, contaminated-case count and held-out threshold protocol are stricter than anything found. This is worth stating in the paper.

## 2. System by system

| # | System (year, source) | Input | What is grouped | Similarity | Algorithm and threshold | Maintained over time | Evaluation |
|---|---|---|---|---|---|---|---|
| 1 | **Oracle lifecycle-aware clustering** (Pattnayak et al., arXiv 2601.04388, Jan 2026) | 90,048 multi-turn cloud-support chats | LLM-extracted "concerns" (~148K), after LLM segmentation into themes | nli-roberta-base-v2 cosine, then UMAP | HDBSCAN within each service group. New concern: **cosine top-5 cluster shortlist, then LLM confirms fit**. Duplicates within a chat removed at cosine 0.95 | **Yes.** Merge candidates at centroid similarity > 0.92 are reviewed by an LLM (31 of 43 approved). Split when cohesion z ≥ 2 (DBI/silhouette). Prune clusters inactive 30 days with < 10 concerns | Silhouette 0.72, DBI 0.46 (+112% silhouette vs KMeans+BERT). LLM matching gives 36% better silhouette than cosine. No pairwise ground truth |
| 2 | **DoorDash KB-gap clustering** (DoorDash engineering blog, 2025) | Chats escalated to a live agent | LLM **summary** of each chat | Open-source embedding, cosine | Online: join the nearest centroid if cosine ≥ τ (swept over **0.70–0.90**), else start a new cluster. Centroid = running mean | Threshold is re-tuned. Human specialists review the generated articles | Business outcome: escalation rate for high-traffic clusters fell from 78% to 43% |
| 3 | **CLAP** (Villarroel et al., ICSE 2016; TSE) | App reviews | Whole reviews, **clustered only within a predicted category** (bug report, feature request) | TF-IDF vector-space cosine (stop words removed, Porter stemming, synonyms deliberately **not** merged) | DBSCAN, minPts = 2, distance = 1 − cosine, **ε = 0.6** tuned on one app (YAHOO) and evaluated on the other apps | None (batch) | MoJoFM vs developer-built clusters: **75%** for bugs, **83%** for features (AR-Miner: 55% and 43%). CLAP is conservative (creates extra singletons), yet ε 0.7–0.9 scored lower because merging became too aggressive |
| 4 | **Hark** (Google, IEEE S&P 2022) | 626M Play reviews, with 6M privacy reviews found by a classifier (AUC 0.92) | **T5-generated issue phrases** (2–4 words) per review | Universal Sentence Encoder cosine | **Leader algorithm** (single pass), with input **sorted by issue frequency** so common issues become the leaders; d_max = 0.9 as reported | Re-run over the corpus; T5 generates the theme title | Human annotation of issue accuracy, coverage and theme quality |
| 5 | **LLM-Cure** (TOSEM 2025, arXiv 2409.15724) | 1.06M reviews of 70 apps | LLM-extracted features (Mixtral) per batch of 1,000 reviews | mistral-embed cosine | Merge features across batches at cosine **≥ 0.75**; stop when the set is stable for 5 batches. Reviews assigned by few-shot LLM | Incremental until convergence | Feature assignment F1 0.80–0.91 |
| 6 | **FeClustRE** (REFSQ 2026, arXiv 2510.18799) | App reviews | Extracted feature phrases | SBERT / Sentence-T5 cosine | **Agglomerative, average linkage**, cut height auto-tuned between 0.1 and 0.9 using silhouette + DBI + cluster-count penalty; LLM (Qwen) labels clusters | Taxonomy merge by label similarity | Silhouette ≈ 0.19, DBI 0.76–1.01; extraction F 0.53 |
| 7 | **Chhetri et al.** (arXiv 2506.10785, 2025) | 894K reviews of AI apps | LLM aspect–sentiment pairs (1.1M), reduced to 168K unique aspects | all-mpnet-base-v2 | k-means, **separately for positive and negative** aspects; k chosen by silhouette | None | Silhouette only |
| 8 | **GitHub feedback tool** (GitHub blog) | Support tickets | Ticket text | BERT embeddings | BERTopic (HDBSCAN); GPT-4 summarises each topic | Periodic re-runs | Qualitative |
| 9 | **Stanik et al.** (RE 2021) | Tweets and user comments | Whole comments | Transformer sentence embeddings | Density clustering with no preset number of clusters | None | Inter-coder agreement up to 98% on cluster cohesion |
| 10 | **ChangeAdvisor** (ICSE 2017) | Reviews (44,683) | Review sentences carrying change requests | Topic model | HDP topic clustering | None | +47% precision, +38% recall vs baseline |
| 11 | **IDEA / MERIT / DIVER / iFeedback** (Tencent/CUHK line, 2018–2022; ASE 2019) | App reviews and WeChat in-app feedback | **Topics or word combinations per time window, not reports** | LDA variants, word embeddings | Online topic models plus anomaly detection per window; iFeedback uses word-combination counts as KPIs | Per version or per window | Emerging-issue precision and recall (DIVER +29.4% P, +32.5% R over IDEA) |
| 12 | **SentiSum, Enterpret, Unwrap** (commercial) | Multichannel feedback | Tags or themes (Enterpret: 5-level "adaptive taxonomy") | Not disclosed | Not disclosed; Unwrap only says it groups "by meaning" | Taxonomy adapts to new themes | Vendor claims only |

**Related empirical finding (ESEM 2025, Jiang et al., WeChat, 50M feedback items):** only 11–67% of feedback is relevant to a system issue, depending on the service. The authors say a relevance filter must run before grouping; their classifier reached F1 = 88.7%.

## 3. Patterns and what they mean for InsightDesk

| Pattern in the literature | Who does it | Our evidence | Suggested change (offline experiment first) |
|---|---|---|---|
| **Normalise text before clustering** (extract a short problem statement) | Hark, Oracle, DoorDash, LLM-Cure, Chhetri | Stock phrases caused about ⅓ of cross-issue errors and ⅔ of contaminated cases | Embed an LLM-extracted "issue statement" (Groq/Qwen, already in the stack) instead of the full cleaned text. Compare pairwise P/R on the original data *with* stock phrases left in |
| **Shortlist, then a strong verifier** | Oracle (top-5 + LLM) | Top-5 retrieval recall is 0.976; the STS-B CE verifier is worse than cosine alone | Replace the STS-B CE with (a) plain cosine, (b) an LLM yes/no judge only for pairs in an uncertain band, or (c) a CE fine-tuned on complaint pairs |
| **Periodic batch merge, split and prune** | Oracle, FeClustRE, BERTopic users | Batch average-linkage F1 is 0.774 vs 0.612 for online (held-out) | Online assignment for real-time cases, plus a scheduled merge pass: candidate case pairs by centroid similarity, then LLM or human approval, as in Oracle's 31/43 |
| **Partition before clustering** | CLAP (by category), Oracle (by service group), Chhetri (by polarity) | Most cross-issue merges come from different products or areas sharing phrasing | Only match candidates within the same product or category (Pinecone metadata filter) |
| **Choose leaders deliberately, not by arrival order** | Hark (frequency-sorted leaders), DoorDash (running-mean centroid) | Medoid and centroid were within arrival-order noise of first-complaint | Low priority; representation is not the bottleneck |
| **Tune the threshold on held-out data, favour conservative settings** | CLAP (tuned on one app, tested on others), DoorDash (sweep) | Our leave-half-issues-out protocol already does this | Keep it, and report it as a methodological strength |
| **Filter irrelevant feedback first** | ESEM 2025 (WeChat) | Not measured (synthetic data has no noise) | Mention as future work for real data |

## 4. How to position this in the paper

- InsightDesk's retrieve-then-verify dedup is in line with the most recent published design (Oracle 2026). Its differences are a cross-encoder verifier instead of an LLM, and cases with report counts rather than topic clusters.
- InsightDesk's evaluation is stricter than prior work: pairwise precision and recall against labelled duplicate issues, contaminated-case counts, and thresholds chosen on held-out issues. Prior systems report MoJoFM (CLAP), intrinsic silhouette and DBI (Oracle, FeClustRE), or business metrics (DoorDash).
- Safe wording: "Unlike topic-level emerging-issue detectors (IDEA, MERIT, DIVER), InsightDesk groups individual complaints into problem-level cases with report counts, and evaluates this grouping against labelled duplicates."

## 5. Gaps and caveats

- The DoorDash original post returned 403; its details come from the ZenML summary (embedding model not named).
- DIVER's full method text was not accessible; it is described only at the level of its abstract and citing papers.
- For Hark, the paper states d_max = 0.9 as a maximum *distance*; whether this is cosine distance on USE embeddings exactly as written was not independently checked.
- The Oracle paper is an arXiv preprint (not yet peer reviewed) and evaluates partly on synthetic data.
- The commercial tools (SentiSum, Enterpret, Unwrap) do not publish their methods.

## Sources

- Oracle: https://arxiv.org/html/2601.04388v1
- DoorDash: https://careersatdoordash.com/blog/doordash-llm-chatbot-knowledge-with-ugc/ ; summary: https://www.zenml.io/llmops-database/automated-knowledge-base-enhancement-using-llms-and-clustering-for-customer-support
- CLAP (TSE version): https://mdipenta.github.io/files/TSE2759112.pdf ; ICSE: https://ieeexplore.ieee.org/document/7886888/
- Hark: https://sranimeshs.github.io/publication/hark/hark.pdf ; https://ieeexplore.ieee.org/document/9833729/
- LLM-Cure: https://arxiv.org/html/2409.15724v1
- FeClustRE: https://arxiv.org/html/2510.18799
- Chhetri et al.: https://arxiv.org/html/2506.10785v1
- GitHub: https://github.blog/ai-and-ml/machine-learning/how-github-harnesses-ai-to-transform-customer-feedback-into-action/
- Stanik et al.: https://arxiv.org/abs/2108.08543
- ChangeAdvisor: https://pasqualesalza.com/publications/PalombaRecommendingLocalizingCode2017.pdf
- DIVER: https://ieeexplore.ieee.org/document/8804432/ ; iFeedback: https://ieeexplore.ieee.org/document/8952229/
- ESEM 2025 (WeChat feedback): https://arxiv.org/html/2508.00593
- Unwrap: https://www.unwrap.ai/post/unwraps-machine-learning ; Enterpret: https://www.enterpret.com/guides/how-to-organize-customer-feedback-with-a-taxonomy
