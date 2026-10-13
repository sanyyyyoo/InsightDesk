# Academic End-to-End User-Feedback / Complaint Analysis Systems Closest to InsightDesk

InsightDesk components used as the coverage rubric:
(a) duplicate/near-duplicate grouping into problem-level cases with report counts; (b) sentiment; (c) topic discovery; (d) per-problem spike/anomaly/emerging-issue detection; (e) automated/LLM root-cause analysis or explanation; (f) human-in-the-loop escalation/routing to departments.

Research note: about 20 search/fetch calls were made. Several Springer, ResearchGate and ScienceDirect full texts returned 403 or login redirects, so some metric numbers come from abstracts or from secondary descriptions (flagged below). Any metric not in the sources below is listed under Gaps rather than guessed.

## Which app-review analysis systems detect emerging/abnormal issues over time, and what do they output/report?

### Takeaway
The CUHK/Tencent line of work (IDEA, ICSE 2018; DIVER, ICSE-SEIP 2019; MERIT/AOBST, TSE 2022) comes closest to InsightDesk's component (d). These systems model topics per app version or time slice and flag topics that differ from earlier slices as "emerging". They then explain each issue with ranked phrases and sentences, not with a root-cause narrative. None of them groups individual reports into cases, and none routes issues to departments.

### Cited Findings

**IDEA (ICSE 2018)**
- Authors: Cuiyun Gao, Jichuan Zeng, Michael R. Lyu, Irwin King. Title: "Online App Review Analysis for Identifying Emerging Issues", ICSE 2018 — [HIT Scholar](https://scholar.hit.edu.cn/en/publications/online-app-review-analysis-for-identifying-emerging-issues/); [ResearchGate](https://www.researchgate.net/publication/329638818_Online_app_review_analysis_for_identifying_emerging_issues)
- Pipeline: AOLDA (Adaptively Online LDA) models version-sensitive topic distributions. An anomaly-detection algorithm over those distributions flags emerging topics. Each topic is labeled with its most relevant phrases and sentences, using a ranking that considers semantic relevance and user sentiment. Results are shown in an interactive "topic river" visualization — [GitHub armor-ai/IDEA](https://github.com/armor-ai/IDEA)
- Input: app reviews with rating, text, title, date, version and nation. A word2vec model was trained on 4M app reviews — [GitHub](https://github.com/armor-ai/IDEA)
- Evaluation: six popular apps from Google Play and the App Store, with official app changelogs as ground truth. 88.9% of the engineers and product managers surveyed said the identified issues help app development. IDEA was applied to several Tencent products — [ResearchGate/abstract](https://www.researchgate.net/publication/329638818_Online_app_review_analysis_for_identifying_emerging_issues)
- Coverage: (a) No, because it groups at the topic level rather than into report-level duplicate cases. (b) Partial, since sentiment is used only in label ranking. (c) Yes (AOLDA). (d) Yes, per version. (e) Partial, since it gives phrase/sentence labels as the explanation. (f) No.

**DIVER (ICSE-SEIP 2019), deployed at WeChat**
- Authors: Cuiyun Gao, Wujie Zheng, Yuetang Deng, David Lo, Jichuan Zeng, Michael R. Lyu, Irwin King. Title: "Emerging App Issue Identification from User Feedback: Experience on WeChat", ICSE-SEIP 2019 — [ACM DL](https://dl.acm.org/doi/abs/10.1109/ICSE-SEIP.2019.00040); [IEEE Xplore](https://ieeexplore.ieee.org/document/8804432/); [PDF](https://www.cse.cuhk.edu.hk/lyu/_media/conference/cgao_icseseip2019_emerging.pdf?id=students:phd&cache=cache)
- Method: extracts emerging word collocations from user feedback. It targets beta-test periods and reports real-time alerts within seconds — [search summary of ACM/Semantic Scholar abstract](https://www.semanticscholar.org/paper/Emerging-App-Issue-Identification-from-User-on-Gao-Zheng/5188eae5d509e1cc69c30098aeea5c582b79361e)
- Results: detected 18 emerging issues in WeChat Android and iOS in one month. It outperformed IDEA by 29.4% in precision and 32.5% in recall — [Semantic Scholar](https://www.semanticscholar.org/paper/Emerging-App-Issue-Identification-from-User-on-Gao-Zheng/5188eae5d509e1cc69c30098aeea5c582b79361e)
- Coverage: (a) Partial, because collocation-based issue groups are not report-level dedup. (b) Not confirmed. (c) Partial. (d) Yes, with real-time alerting. (e) No. (f) No; it produces alerts, but no routing workflow was found.

**MERIT / AOBST (IEEE TSE 2022; arXiv 2020)**
- Authors: Cuiyun Gao, Jichuan Zeng, Zhiyuan Wen, David Lo, Xin Xia, Irwin King, Michael R. Lyu. Title: "Emerging App Issue Identification via Online Joint Sentiment-Topic Tracing", published in TSE 48(08):3025–3043 — [arXiv 2008.09976](https://arxiv.org/abs/2008.09976); [search result citing TSE](https://www.researchgate.net/publication/351178591_Emerging_App_Issue_Identification_via_Online_Joint_Sentiment-Topic_Tracing)
- Method: the Adaptive Online Biterm Sentiment-Topic (AOBST) model jointly models topics and sentiment across app versions. It infers negatively reflected topics per version and interprets them with the most relevant phrases and sentences — [arXiv](https://arxiv.org/abs/2008.09976)
- Emerging-topic definition: anomalies are topics that show "obvious differences with the counterparts in the previous versions" — [arXiv PDF](https://arxiv.org/pdf/2008.09976)
- Result: F1 is 22.3% higher than IDEA, evaluated on Google Play and App Store apps — [arXiv](https://arxiv.org/abs/2008.09976)
- Coverage: (a) No. (b) Yes, through joint sentiment-topic modeling. (c) Yes. (d) Yes, per version. (e) Partial, through phrase/sentence interpretation. (f) No.

**AOBTM (arXiv 2020)**
- Authors: Mohammad Abdul Hadi, Fatemeh H. Fard. AOBTM is an adaptive online biterm topic model for short texts. It uses an optimal number of previous time slices and auto-selects the number of topics. It reports more coherent topics than state-of-the-art baselines on app reviews and other short-text sets; the abstract gives no numbers — [arXiv 2009.09930](https://arxiv.org/abs/2009.09930)
- Coverage: (a) No. (b) No. (c) Yes. (d) Partial, because it models topics over time and is used as an input to emerging-issue detection. (e) No. (f) No.

**AR-Miner (ICSE 2014)**
- AR-Miner filters non-informative reviews with EMNB (semi-supervised Naive Bayes) and groups the informative ones with LDA. It then ranks the groups by rating, review fluctuation over time, and volume of similar reports — [search result summarizing the survey](https://www.sciencedirect.com/science/article/pii/S0957417418303361); the PeerJ mapping study lists it as 2014, using LDA/ASUM — [PeerJ/PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11623114/)
- Coverage: (a) Partial, because it groups by topic and counts volume. (b) No. (c) Yes. (d) Partial, because temporal fluctuation feeds the ranking but it does not detect spikes. (e) No. (f) No.

**Survey-level comparison**
- The PeerJ 2024 mapping study states that "KEFE, MERIT, DIVER, SAFER, SIRA, T-FEX, RE-BERT, and AOBTM outperformed baseline tools like IDEA and SAFE" — [PMC11623114](https://pmc.ncbi.nlm.nih.gov/articles/PMC11623114/)

### Inferences
- The closest academic analog to InsightDesk's (d) is DIVER, which is industrial, near-real-time and alert-oriented. InsightDesk differs by running z-score spike detection per deduplicated case over 6-hour windows. The academic systems detect emergence per topic, per app version, or per time slice, so InsightDesk's per-case granularity appears novel relative to them.
- The "explanations" in these systems are extractive: representative phrases and sentences. None generates a grounded structured RCA of the kind InsightDesk does with LLM JSON output.

### Gaps
- No primary sources were fetched for PUMA, SURF metrics, ReviewSpotlight, MARA, Wiscom, TOUR or KEFE metrics. SURF (2017) and KEFE (2021) appear only in the mapping study table, without numbers — [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11623114/)
- IDEA's precision, recall and F1 numbers were not recovered, because the full text was not accessible.
- The Springer Software Quality Journal paper "Issue detection and prioritization based on mobile application reviews" (2024) is relevant to (a)+(d) but its full text was blocked, so authors and metrics are unverified — [Springer](https://link.springer.com/article/10.1007/s11219-024-09703-2)

## Which works cluster reviews/complaints into issue-level groups with counts, and do any do duplicate grouping of individual reports?

### Takeaway
CLAP (ICSE 2016 / TSE) and ChangeAdvisor (ICSE 2017) explicitly cluster individual reviews that report the same bug or request. They are the closest academic precedent for InsightDesk's (a) duplicate-case grouping, although they use DBSCAN or topic clustering rather than retrieval plus cross-encoder verification. Hark (Google, IEEE S&P 2022) produces a theme → issue hierarchy with representative reviews.

### Cited Findings

**CLAP**
- Authors: Villarroel, Bavota et al. Title: "Release Planning of Mobile Apps Based on User Reviews" (ICSE 2016); extended as "Listening to the Crowd for the Release Planning of Mobile Apps" (TSE) — [Semantic Scholar](https://www.semanticscholar.org/paper/Release-Planning-of-Mobile-Apps-Based-on-User-Villarroel-Bavota/8204559805f2b45b43ce17efcb8adc6b631d9dca); [TSE PDF](https://mdipenta.github.io/files/TSE2759112.pdf)
- Method: classifies reviews (bug report, feature suggestion, other) with Random Forest. It then clusters related reviews with DBSCAN, e.g. "all reviews reporting the same bug", and prioritizes the clusters for the next release. Reported overall accuracy is 86.0% (secondary description) — [search result summary citing the helpful app review summarization paper](https://arxiv.org/pdf/2210.06235)
- Coverage: (a) Yes, since it clusters same-bug reviews and cluster sizes feed prioritization. (b) No. (c) Partial, through category classification. (d) No. (e) No. (f) Partial, because the output is release-planning prioritization, not department routing.

**ChangeAdvisor (ICSE 2017)**
- Authors: Palomba et al. Title: "Recommending and Localizing Change Requests for Mobile Apps Based on User Reviews" — [ResearchGate](https://www.researchgate.net/publication/313428459_Recommending_and_Localizing_Change_Requests_for_Mobile_Apps_Based_on_User_Reviews); [PDF](https://pasqualesalza.com/publications/PalombaRecommendingLocalizingCode2017.pdf)
- Method: clusters similar user change requests and localizes the source-code components they affect. It was evaluated on 44,683 reviews of 10 open-source apps. Localization reached 81% precision and 70% recall, which is +47% precision and +38% recall over the baseline — [search summary of paper](https://www.researchgate.net/publication/313428459_Recommending_and_Localizing_Change_Requests_for_Mobile_Apps_Based_on_User_Reviews)
- Coverage: (a) Yes, by clustering similar requests. (b) No. (c) Partial. (d) No. (e) Partial, since code localization is a form of root-cause localization. (f) No.

**Hark (Google)**
- Authors: Hamza Harkous, Sai Teja Peddinti, Rishabh Khandelwal, Animesh Srivastava, Nina Taft. Title: "Hark: A Deep Learning System for Navigating Privacy Feedback at Scale", IEEE S&P 2022. The prompt described it as a 2023 feedback-analysis system; the source says S&P 2022 — [Google Research](https://research.google/pubs/pub51307/)
- Pipeline: privacy-feedback classification, then issue generation, then theme creation, then summaries. The output is a hierarchy of themes and fine-grained issues with representative reviews. It ran over 626M Google Play reviews, extracted 6M privacy reviews at AUC-ROC 0.92, and covered 1.3M apps — [Google Research](https://research.google/pubs/pub51307/)
- Coverage: (a) Partial, because it groups reviews into issues with representatives; exact duplicate counting is not described. (b) No evidence. (c) Yes. (d) No evidence. (e) Partial, through generated issue summaries. (f) No.

**FeClustRE (REFSQ 2026)**
- FeClustRE combines hybrid syntactic plus LLM feature extraction, hierarchical clustering with auto-tuning, and LLM semantic taxonomy labels. It was evaluated on public extraction benchmarks and on reviews of generative-AI assistant apps; no numbers were retrieved — [arXiv 2510.18799](https://arxiv.org/abs/2510.18799); [REFSQ 2026](https://2026.refsq.org/details/refsq-2026-research-papers/13/FeClustRE-Hierarchical-Clustering-and-Semantic-Tagging-of-App-Features-from-User-Rev)
- Coverage: (a) Partial, since it clusters at feature level. (b) No. (c) Yes. (d) No. (e) No. (f) No.

### Inferences
- Among the sources found, only CLAP explicitly describes grouping individual reports of "the same bug". No academic app-review system found uses a two-stage bi-encoder retrieval plus cross-encoder verification step for deduplication. InsightDesk's dedup stage therefore resembles duplicate-bug-report detection more than app-review mining.

### Gaps
- SUR-Miner, MARK and GuMa cluster reviews by aspects or keywords (listed in [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11623114/)), but no metrics were retrieved.
- CLAP's clustering-specific metrics (e.g., MoJoFM) were not retrieved from the primary PDF.

## Which academic complaint management / consumer complaint systems combine classification/clustering + trend/spike detection + routing?

### Takeaway
Academic complaint systems mostly do classification plus routing (component f), sometimes with sentiment-based prioritization. None found combines duplicate grouping, spike detection and root-cause explanation. The CFPB-based works found are largely classification or predictive studies and GitHub projects rather than peer-reviewed end-to-end systems.

### Cited Findings
- **NLP-based grievance redressal for Indian Railways** (Rawat and Kaushik, arXiv 2021). A plugin that identifies complaints in tweets to Indian Railways to support the existing 24/7 manual Twitter handling. The search summary says it categorizes complaints and assigns them to divisions, regions and departments. The fetched abstract did not show models or metrics — [arXiv 2111.08999](https://arxiv.org/abs/2111.08999)
- **Decision support grievance redressal system using sentence sentiment analysis** (ACM). Pre-processes grievances with text mining and scores their negativity using sentence sentiment, supporting prioritization — [ACM](https://dl.acm.org/doi/pdf/10.1145/3428502.3428505) (search snippet only)
- **Semantic-Based Analysis in Complaint Management System with Analytics**. Uses text mining and clustering, with semantic analysis choosing the department to route to (search snippet only; the venue is unclear, and academia.edu is a low-quality source) — [academia.edu](https://www.academia.edu/115189005/_Semantic_Based_Analysis_in_Complaint_Management_System_with_Analytics_)
- **Automated Classification of Public Transport Complaints via Text Mining Using LLMs and Embeddings** (MDPI Information 2025, 16(8):644). Uses LLMs and embeddings, plus unsupervised clustering (HDBSCAN, UMAP) for fine-grained groups — [MDPI](https://www.mdpi.com/2078-2489/16/8/644)
- **CitySolution** (arXiv 2024). Deep-learning classification of citizen complaints (e.g., "Damaged Road", "Flood", "Trash") to distribute tasks to city-corporation departments — [arXiv 2410.12882](https://arxiv.org/pdf/2410.12882)
- **CFPB**. "Predictive Analysis of CFPB Consumer Complaints Using Machine Learning" — [arXiv 2407.06399](https://arxiv.org/abs/2407.06399); "CFPB Consumer Complaints Analysis Using Hadoop" — [arXiv 2310.06076](https://arxiv.org/pdf/2310.06076). The CFPB routing, sentiment and theme systems found (Complaint-Router, doc-routing-cfpb, ConsumerShield) are GitHub projects, not peer-reviewed work — [Complaint-Router](https://github.com/srummanf/Complaint-Router); [ConsumerShield](https://github.com/ayushicarpenter2028/ConsumerShield)
- **Customer-temperament-centered complaint handling system** with a new complaint dataset (Advanced Engineering Informatics, ScienceDirect 2024) — [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S147403462400168X) (abstract not fetched)

### Inferences
- Complaint-management research covers (f) routing and sometimes (b) sentiment. App-review research covers (c) and (d). InsightDesk's combination of both families, with LLM RCA, was not found in any single academic system.

### Gaps
- Metric numbers for the grievance, public-transport and CitySolution systems were not retrieved.
- No academic telecom, banking or e-commerce complaint system with spike detection was found within the search budget.

## Which 2023-2026 papers use LLMs for end-to-end user-feedback analytics?

### Takeaway
LLM work so far targets feature assignment and improvement suggestions (LLM-Cure), taxonomy labeling (FeClustRE), classification plus aspect-sentiment plus topic clustering (Chhetri et al. 2025), and whether feedback can detect issues at all (Jiang et al., ESEM 2025). None found performs grounded per-issue root-cause explanation tied to spike detection.

### Cited Findings
- **LLM-Cure** (Maram et al., ACM TOSEM 2025; arXiv 2409.15724). Assigns features to reviews with an LLM. For a complaint, it retrieves highly rated (4–5 star) competitor reviews on the same feature and proposes improvements. It was evaluated on 1,056,739 reviews of 70 Android apps. Feature assignment beat the state of the art by up to 13% F1, 16% recall and 11% precision, and 73% of its suggestions were implemented — [arXiv](https://arxiv.org/html/2409.15724v2); [ACM](https://dl.acm.org/doi/10.1145/3744644); [PDF](https://seal-queensu.github.io/publications/pdf/TOSEM-Maram-2025.pdf)
  - Coverage: (a) No. (b) Partial, since it uses star ratings. (c) Partial, through feature assignment. (d) No. (e) Partial, since it suggests fixes but does not diagnose root cause. (f) No.
- **"What Users Value and Critique"** (Chhetri, Upadhyay, Siddique, Farooq; arXiv June 2025). An LLM classification, aspect-sentiment extraction and topic-clustering pipeline over 894K reviews of 292 AI apps. It produced more than 1M aspect-sentiment pairs, clustered into 18 positive and 15 negative topics — [arXiv 2506.10785](https://arxiv.org/abs/2506.10785)
  - Coverage: (a) No. (b) Yes. (c) Yes. (d) No. (e) No. (f) No.
- **"Can User Feedback Help Issue Detection?"** (Jiang, Gu, Zheng, Zhou, Lyu; ESEM 2025). An empirical study of 50,378,766 feedback items from six services of a one-billion-user platform. It finds that much feedback is irrelevant to system issues, so filtering is essential. Some severe issues cannot be identified from feedback characteristics alone, and topic distributions stay consistent over time — [arXiv 2508.00593](https://arxiv.org/abs/2508.00593)
- **"Automatic Analysis of App Reviews Using LLMs"** (SciTePress 2025). Classifies reviews into bug report, feature request, user experience and rating; GPT-3.5 reached F1 0.849 (search snippet) — [SciTePress](https://www.scitepress.org/Papers/2025/133756/133756.pdf)
- **"Semantic Feedback Processing with LLMs: Automating Issue Detection and Prioritization in DevOps"** (Procedia Computer Science 2025). Its claims about improved triage efficiency come from a search snippet only, since the page returned 403 — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1877050925030145)
- **ASTRA — Agentic System for Ticket Resolution and Analysis** (arXiv 2026). Relevant to LLM ticket triage; not fetched — [arXiv 2608.28790](https://arxiv.org/pdf/2608.28790)
- LLM-agent RCA exists for cloud incidents (Roy et al., FSE Companion 2024), not for user feedback — [ACM](https://dl.acm.org/doi/10.1145/3663529.3663841); [arXiv 2403.04123](https://arxiv.org/html/2403.04123v1)

### Inferences
- LLM-based RCA over user complaints appears to be an open niche. The closest analogs are incident-RCA LLM agents from AIOps, which work on telemetry rather than on customer text.

### Gaps
- No peer-reviewed paper was found that does LLM RCA directly from clustered customer complaints.
- The DevOps LLM feedback paper and ASTRA need full-text checks for which (a)–(f) components they cover.

## Are there surveys/SLRs listing end-to-end tools?

### Takeaway
Two surveys are useful for finding candidates: Dąbrowski et al.'s SLR (EMSE 2022, 182 papers from 2012–2020) and the PeerJ 2024 mapping study, which catalogs 48 tools.

### Cited Findings
- Dąbrowski, Letier, Perini, Susi, "Analysing app reviews for software engineering: a systematic literature review", EMSE 27(2), article 43, 2022. It covers 182 papers from 2012–2020 and classifies them by mined information, techniques and SE activity (DOI 10.1007/s10664-021-10065-7) — [UCL Discovery](https://discovery.ucl.ac.uk/id/eprint/10143231/); [PDF](https://discovery.ucl.ac.uk/10143231/1/Letier_AnalysingAppReviewsForSoftware.pdf)
- Massenon et al., "Mobile app review analysis for crowdsourcing of software requirements: a mapping study of automated and semi-automated tools", PeerJ Computer Science 2024. It catalogs 48 tools, including AR-Miner (2014), GuMa (2014), MARK (2015), CRISTAL (2015), SUR-Miner (2015), SAFE (2017), URR (2017), SURF (2017), IDEA (2018), CLAP (listed as 2019), SAFER (2019), KEFE (2021), SIRA (2022) and T-FREX (2024) — [PMC11623114](https://pmc.ncbi.nlm.nih.gov/articles/PMC11623114/)
- Earlier survey: "Extracting useful software development information from mobile application reviews: A survey of intelligent mining techniques and tools", Expert Systems with Applications 2018 — [ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0957417418303361)
- For public-sector feedback: "Application of Text Analytics in Public Service Co-Creation: Literature Review and Research Framework" — [arXiv 2305.18316](https://arxiv.org/pdf/2305.18316)

### Inferences — ranked list of systems closest to InsightDesk

| Rank | System (year, venue) | a dedup cases | b sentiment | c topics | d spikes/emerging | e RCA/explain | f routing | Key lack vs InsightDesk |
|---|---|---|---|---|---|---|---|---|
| 1 | DIVER (2019, ICSE-SEIP) | Partial | ? | Partial | Yes (real-time) | No | No (alerts only) | No report-level dedup, RCA or routing |
| 2 | MERIT/AOBST (2022, TSE) | No | Yes | Yes | Yes (per version) | Partial (phrases) | No | Per-version, not per-case windows; extractive explanation |
| 3 | IDEA (2018, ICSE) | No | Partial | Yes | Yes (per version) | Partial | No | Same as MERIT; LDA-based |
| 4 | CLAP (2016, ICSE / TSE) | Yes (DBSCAN same-bug) | No | Partial | No | No | Partial (prioritization) | No time or spike analysis, sentiment or RCA |
| 5 | AR-Miner (2014, ICSE) | Partial | No | Yes | Partial (fluctuation in ranking) | No | No | No true spike detection or RCA |
| 6 | ChangeAdvisor (2017, ICSE) | Yes (clusters) | No | Partial | No | Partial (code localization) | No | No temporal analysis |
| 7 | Hark (2022, IEEE S&P) | Partial | ? | Yes | ? | Partial (summaries) | No | Privacy-only; no spikes or routing |
| 8 | Chhetri et al. (2025, arXiv) | No | Yes | Yes | No | No | No | Static corpus analysis |
| 9 | LLM-Cure (2025, TOSEM) | No | Partial | Partial | No | Partial (fix suggestions) | No | Competitor focus |
| 10 | Grievance/complaint routing (Indian Railways 2021; CitySolution 2024) | No | Partial | Partial | No | No | Yes | No clustering, spikes or RCA |

- No academic system covering all six components was found. Systems 1–3 cover (c)+(d), 4 and 6 cover (a), and 10 covers (f).

### Gaps
- The Dąbrowski SLR's tool list was not extracted in detail.
- The Genc-Nayebi & Abran survey was not retrieved.
- PUMA, ReviewSpotlight, MARA, Wiscom and TOUR were not verified in this pass.
