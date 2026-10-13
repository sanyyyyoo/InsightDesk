# AIOps / Incident Management and 2023-2026 LLM Analytics Systems Adjacent to InsightDesk

Scope: systems that link customer-reported signals (tickets, feedback, support conversations) into problems, detect surges, and explain causes, compared against InsightDesk's capabilities (a) dedup into problem-level cases with report counts, (b) sentiment, (c) topic discovery, (d) per-problem spike/emerging-issue detection, (e) LLM/automated RCA, (f) human-in-the-loop escalation/routing.

Legend for coverage: Y = yes, P = partial, N = no. INPUT: CUST = customer-written text; TELEM = machine telemetry (alerts, KPIs, logs, monitors); MIX = both.

## Which Microsoft/industry AIOps systems ingest CUSTOMER text, and how do they dedup, detect surges, and explain causes?

### Takeaway
The only AIOps systems in the list that take customer-written text as their main input are iPACK, LinkCM, iFeedback (and DIVER), MID, TickIt (ByteDance) and, arguably, AidAI. Of these, **TickIt (ByteDance Volcano Engine, 2025)** is the closest to InsightDesk. It does LLM escalation, embedding-based dedup of tickets onto the same underlying issue, topic-aware routing and human feedback. However, it has no sentiment analysis, topic discovery, per-problem z-score spike detection or grounded RCA. RCACopilot, Nissist, X-lifecycle, Oasis and DeepTriage work on telemetry or engineer-written incidents, not on customer complaints.

### Cited Findings

**iPACK: Incident-aware Duplicate Ticket Aggregation (Microsoft Azure, ICSE 2023). INPUT: MIX (customer support tickets plus cloud-side alerts/incidents)**
- Aggregates duplicate customer support tickets by fusing customer-side tickets with cloud-side incidents. It targets the case where duplicate tickets "carry semantically different descriptions due to complex service dependency", so plain text similarity fails. — [arXiv 2302.09520](https://arxiv.org/abs/2302.09520); [MSR page](https://www.microsoft.com/en-us/research/publication/incident-aware-duplicate-ticket-aggregation-for-cloud-systems/)
- Methods: graph-based incident profiling (GIP), which models alert-alert relations, and an attentive interaction network (AIN), which models alert-ticket relations. — [IEEE Xplore](https://ieeexplore.ieee.org/document/10172621/)
- Evaluated on three production Azure datasets: F1 0.871-0.935, which is 12.4%-31.2% better than existing approaches. — [arXiv 2302.09520](https://arxiv.org/abs/2302.09520)
- In deployment, support engineers used it to start batch communications with potentially impacted customers and avoid duplicate manual inspection. — [IEEE Xplore](https://ieeexplore.ieee.org/document/10172621/)
- Coverage: (a) Y, as ticket aggregation; (b) N; (c) N; (d) N, because incidents come from telemetry alerts rather than ticket surges; (e) P, since it links tickets to an incident but does not generate an explanation; (f) P, since it enables batch customer communication.
- Lacks vs InsightDesk: it needs cloud-side alert telemetry; it has no sentiment, topic modelling, per-case spike detection or LLM RCA.

**LinkCM: Efficient Customer Incident Triage via Linking with System Incidents (Microsoft, Gu et al., 2020). INPUT: MIX (customer incidents plus monitor-reported system incidents)**
- A learning-based approach that automatically links customer incidents to system incidents reported by monitors, using transfer learning to reduce data needs. — [MSR page](https://www.microsoft.com/en-us/research/publication/efficient-customer-incident-triage-via-linking-with-system-incidents/)
- An empirical study on 7 real cloud service systems found that adding system-incident information speeds up customer-incident triage by 13.1x on average. — [MSR page](https://www.microsoft.com/en-us/research/publication/efficient-customer-incident-triage-via-linking-with-system-incidents/)
- A later WeChat study describes LinkCM as "linking user-reported issues to system KPIs". — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)
- Coverage: (a) P, indirect grouping through a shared system incident; (b) N; (c) N; (d) N; (e) P, link to a known incident; (f) P, triage.

**MID: Efficient Incident Identification from Multi-dimensional Issue Reports via Meta-heuristic Search (Microsoft, ESEC/FSE 2020). INPUT: customer issue reports, but only their categorical attributes (not free text)**
- Treats incident detection over large volumes of multi-dimensional issue reports as a combinatorial optimisation problem. A meta-heuristic search finds the attribute combinations that indicate an incident, and it "significantly outperforms" the prior state of the art on synthetic and production cloud data. — [FSE 2020 page](https://2020.esec-fse.org/details/fse-2020-papers/167/Efficient-Incident-Identification-from-Multi-dimensional-Issue-Reports-via-Meta-heuri); [dblp](https://dblp.org/rec/conf/sigsoft/GuLQQL0LDCWZCZ20.html)
- A follow-up, "Adaptive Anomaly Detection for Multi-Dimensional Issue Reports", appears in ACM TOSEM. — [ACM DL](https://dl.acm.org/doi/10.1145/3801155)
- Coverage: (d) Y, as surge detection over report attributes, which is the closest analogue to InsightDesk's spike detection. (a) N, (b) N, (c) N, (e) P (the attribute combination acts as a localisation), (f) N.

**iFeedback (ASE 2019) and DIVER (2019). INPUT: CUST (user feedback text / app reviews)**
- iFeedback does real-time issue detection from user feedback text. It extracts word-combination-based indicators and runs anomaly detection over them, favouring speed over heavy NLP, as a "system life-condition monitor". It targets issues that backend monitoring misses, such as UI bugs, low-impact bugs and third-party errors. — [IEEE Xplore](https://ieeexplore.ieee.org/document/8952229/); [ASE 2019](https://2019.ase-conferences.org/details/ase-2019-papers/13/iFeedback-Exploiting-User-Feedback-for-Real-time-Issue-Detection-in-Large-Scale-Onli)
- Later work notes it was deployed in real systems but that "the accuracy of its detection results is relatively low". — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)
- DIVER (Gao et al., 2019) identifies emerging issues using word collocations. — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)
- Coverage (iFeedback): (a) P, since indicators act as implicit issue groups; (b) N; (c) P; (d) Y, surge detection on text indicators; (e) N; (f) N.
- Lacks vs InsightDesk: no semantic (embedding) dedup into problem cases, no sentiment, no LLM RCA, no escalation workflow.

**"Can User Feedback Help Issue Detection?" empirical study (WeChat/Tencent, arXiv 2508.00593, 2025). INPUT: CUST**
- Covers 50.3M feedback items over one year from 6 WeChat services. Only 10.94%-66.54% of feedback items reported real system issues, and most services were below 30%, which motivates noise filtering. — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)
- Text features such as sentiment and length were poor predictors of issue severity. Some severe issues, such as crashes, received very few reports. — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)
- A BERT + TextCNN classifier reached 89.58% accuracy and 88.71% F1 at detecting issue-relevant feedback. Topic distributions were stable across versions (Wasserstein distance). — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)
- It concludes that feedback "is not what we can entirely rely on" and should be combined with monitoring. — [arXiv 2508.00593](https://arxiv.org/html/2508.00593)

**TickIt: LLM-based Automated Ticket Escalation (ByteDance Volcano Engine, arXiv 2504.08475, 2025). INPUT: CUST (ticket title, description and customer-analyst dialogue)**
- Data: 20,066 tickets (654,901 messages), Aug-Dec 2024. — [arXiv 2504.08475](https://arxiv.org/html/2504.08475)
- Functions:
  - Multi-class escalation (system failures, customer complaints, asset loss) using a Chain-of-Thought LLM (Doubao).
  - Deduplication of tickets tied to the same underlying issue, using embedding similarity with a threshold plus LLM "issue rewriting".
  - Topic-aware routing to on-call engineers, customer managers or security.
  - Dynamic re-analysis as conversations evolve.
  - SFT with LoRA using upvote/downvote human feedback.
  - Source: [arXiv 2504.08475](https://arxiv.org/html/2504.08475)
- Escalation: SFT+CoT reached F1 0.862 (P 81.8%, R 91.2%). The best small-model baseline reached F1 0.801 and Llama3.1-70B reached F1 0.816. — [arXiv 2504.08475](https://arxiv.org/html/2504.08475)
- Dedup: F1 0.879 at threshold 0.88. Issue rewriting added +1.7% F1 overall and +6.1% on multi-linked tickets. — [arXiv 2504.08475](https://arxiv.org/html/2504.08475)
- Deployment: 2,012 tickets escalated, 81% of feedback marked the escalation appropriate, MTTR fell 39%, and about 10 person-days of analyst time were saved per day. — [arXiv 2504.08475](https://arxiv.org/html/2504.08475)
- Coverage: (a) Y; (b) N, though "customer complaints" is an escalation category rather than sentiment scoring; (c) P, predefined topics rather than discovered ones; (d) N; (e) N/P, CoT rationale for escalation but no RCA; (f) Y.
- Lacks vs InsightDesk: no unsupervised topic discovery, no sentiment model, no per-case volume anomaly detection, no grounded root-cause JSON. It uses a proprietary LLM and private data.

**AidAI: Automated Incident Diagnosis for AI Workloads in the Cloud (Microsoft, arXiv 2506.01481, 2025). INPUT: MIX (customer-described problem plus diagnostic telemetry)**
- A "customer-centric" system that diagnoses customer incidents immediately and streamlines ticket creation for unresolved ones. It mimics on-call engineer reasoning over a failure taxonomy (LlamaIndex, anytree, GPT-4o by default). — [arXiv 2506.01481](https://arxiv.org/pdf/2506.01481)
- Motivation: median time to mitigate in Microsoft's AI infrastructure was 52.5 hours. Results: Micro-F1 0.854 and Macro-F1 0.816, about 60% less verification time, average diagnosis time 304 s. The numbers come via a secondary summary and should be checked against the PDF. — [themoonlight review](https://www.themoonlight.io/en/review/aidai-automated-incident-diagnosis-for-ai-workloads-in-the-cloud); [arXiv PDF](https://arxiv.org/pdf/2506.01481)
- Coverage: (a) N; (b) N; (c) N; (d) N; (e) Y, per-incident diagnosis; (f) P, ticket creation.

**Telemetry and engineer-incident systems (NOT customer text)**
- **RCACopilot (Microsoft, EuroSys 2024). INPUT: TELEM plus incident records.**
  - Matches incoming incidents to handlers by alert type, gathers runtime diagnostics, predicts the root-cause category and generates an explanatory narrative with an LLM.
  - RCA accuracy is up to 0.766 on Microsoft data. The diagnostic-collection component has been in use for more than 4 years.
  - Coverage: (e) Y, (f) P.
  - Sources: [arXiv 2305.15778](https://arxiv.org/pdf/2305.15778); [ACM DL](https://dl.acm.org/doi/10.1145/3627703.3629553)
- **Oasis: "Assess and Summarize: Improve Outage Understanding with LLMs" (Microsoft, ESEC/FSE 2023 Industry). INPUT: TELEM/incidents.**
  - Assesses outage impact scope by aggregating related incidents, then summarises the outage with fine-tuned GPT-3.x.
  - Evaluated on 3 years of data from 18 major Microsoft cloud systems. Its summaries are 251x faster than humans.
  - Coverage: (a) P, grouping incidents into an outage; (e) P, summary.
  - Sources: [arXiv 2305.18084](https://arxiv.org/abs/2305.18084); [MSR page](https://www.microsoft.com/en-us/research/publication/assess-and-summarize-improve-outage-understanding-with-large-language-models/)
- **X-lifecycle Learning (Microsoft, FSE 2024 Industry). INPUT: TELEM plus SDLC artefacts.**
  - Augments LLM context with code, config, monitors, dependencies and TSGs.
  - Tasks: root-cause recommendation for dependency-failure incidents and ontology of service monitors, on 353 incidents and 260 monitors.
  - The abstract claims improvement over SOTA but gives no numbers.
  - Source: [arXiv 2404.03662](https://arxiv.org/abs/2404.03662)
- **Nissist (Microsoft, ECAI 2024 Demo). INPUT: TSGs plus incident mitigation history, engineer-facing.**
  - A multi-agent LLM copilot that suggests mitigations. It "significantly reduces" time to mitigate in user experiments, but no number appears in the abstract.
  - Sources: [arXiv 2402.17531](https://arxiv.org/abs/2402.17531); [ADS](https://ui.adsabs.harvard.edu/abs/2024arXiv240217531A/abstract)
- **DeepTriage (Microsoft Azure, KDD 2020). INPUT: incident records.**
  - An ensemble of gradient boosting, clustering and DNNs that recommends the responsible team.
  - F1 82.9%, and 76.3%-91.3% on highly impacted incidents. Deployed in Azure since Oct 2017.
  - Coverage: (f) Y, routing.
  - Sources: [arXiv 2012.03665](https://arxiv.org/pdf/2012.03665); [ACM DL](https://dl.acm.org/doi/10.1145/3394486.3403380)
- **Microsoft Research blog** on LLMs for automatic cloud incident management, as background. — [MSR blog](https://www.microsoft.com/en-us/research/blog/large-language-models-for-automatic-cloud-incident-management/)
- **Curated list** of cloud incident literature. — [yinfangchen/cloud-incident-lit](https://github.com/yinfangchen/cloud-incident-lit)

### Inferences
- The Microsoft/Tencent line of work splits the problem the same way InsightDesk does. Customer text is used for detection and dedup (iFeedback, MID, iPACK, LinkCM). Telemetry plus LLMs is used for RCA (RCACopilot, X-lifecycle, Nissist). No single published system found combines customer-text dedup, sentiment, topic discovery, per-problem spike detection, LLM RCA and a human-approved escalation. InsightDesk's novelty is the integration and doing RCA from complaint text alone. It is not novel in any single component.
- InsightDesk's grounded LLM RCA works from customer text without telemetry. That is weaker evidence than RCACopilot/AidAI, which ground in diagnostics. InsightDesk should call its output a "hypothesised cause" or "explanation", not a verified root cause.
- The WeChat finding (sentiment and length do not predict severity; 10.94%-66.54% of feedback is issue-relevant) is a direct caution for InsightDesk. It suggests adding an issue-relevance filter and not using sentiment as a severity proxy.
- TickIt's dedup F1 of 0.879 and iPACK's 0.871-0.935 are the most comparable published dedup numbers. Both are on proprietary data.

### Gaps
- "Dependency Aware Incident Linking in Large Cloud Systems" (2024), TSGuard, and a paper titled "Detecting Customer-Impacting Incidents" could not be verified. I found no primary source with details or numbers.
- The LinkCM venue is unconfirmed, and its precision/F1 numbers were not retrieved. Only the 13.1x triage speed-up was found.
- The full iFeedback precision/recall numbers were not retrieved.
- The AidAI numbers come from a secondary review site, not the PDF.

## Customer-issue surge detection from support tickets or customer reports at cloud/telecom/SaaS providers

### Takeaway
Published evidence of ticket-surge detection is mostly from Microsoft (MID on issue-report attributes) and Tencent (iFeedback on WeChat feedback). Commercial ITSM tools (ServiceNow Predictive Intelligence clustering) market "cluster similar incidents, then alert on a major incident", which conceptually matches InsightDesk's (a)+(d). I found no peer-reviewed Alibaba, Huawei, Amazon, Salesforce or Google paper specifically on customer-ticket surge detection.

### Cited Findings
- ServiceNow Predictive Intelligence's Clustering framework groups similar records by textual patterns to find major incidents and trending issues. Community documentation gives the example "if 50 users report 'Skype call drop' in 10 minutes, clustering algorithms group these incidents and alert Problem Management". This is vendor/community material, not peer-reviewed, and no accuracy numbers are given. — [ServiceNow community](https://www.servicenow.com/community/platform-analytics-forum/predictive-intelligence-in-servicenow-20-real-time-use-cases/m-p/3444290); [ServiceNow product page](https://www.servicenow.com/products/predictive-intelligence.html)
- Aisera documents incident/ticket clustering as a way to identify major issues and problems. This is vendor documentation. — [Aisera docs](https://docs.aisera.com/ai-ops/incident-ticket-clustering)
- A news report says Alibaba Cloud's DualLane system routes "fast path" inquiries to templates and finds clusters of similar issues in the "slow lane" that may warrant elevation. This is press coverage, not a paper. — [The Register](https://www.theregister.com/ai-and-ml/2026/08/11/alibaba-cloud-is-using-ai-to-help-it-use-less-ai/5285815)
- MID (Microsoft) detects incidents as anomalous attribute combinations in customer issue reports. — [FSE 2020](https://2020.esec-fse.org/details/fse-2020-papers/167/Efficient-Incident-Identification-from-Multi-dimensional-Issue-Reports-via-Meta-heuri)
- "Smart Issue Detection for Large-Scale Online Service Systems Using Multi-Channel Data" (Springer) is a related multi-channel issue-detection work; its details were not retrieved. — [Springer](https://link.springer.com/chapter/10.1007/978-3-031-57259-3_8)

### Inferences
- InsightDesk's per-case z-score over 6-hour windows is simpler than MID's attribute-combination search or iFeedback's learned anomaly detection. It is, however, a reasonable baseline, and those papers are the right comparators for justifying it.

### Gaps
- I found no primary source for customer-ticket surge detection at Huawei, Amazon, Salesforce or Google SRE. The Google SRE customer-report practice was not searched in depth.
- ServiceNow publishes no evaluation numbers for its clustering.

## 2023-2026 LLM papers for customer support and feedback analytics: which combine several of (a)-(f)?

### Takeaway
LLM clustering and topic work (TopicGPT, LLooM, GoalEx, k-LLMmeans, Dial-In LLM, the FLAIRS ABCD study, RAILS) covers (a) and (c) well, and RAILS is deployed for SaaS ticket topic discovery. None of these adds sentiment, surge detection, RCA and escalation together. TickIt is the only LLM system found that combines (a) and (f) on customer tickets in production.

### Cited Findings
- **LLM-Augmented Clustering for Customer Support Ticket Triage: A Comparative Study on the ABCD Dataset** (FLAIRS 2026). An LLM extracts normalised issue statements before embedding and clustering, applied to the ABCD customer-service dataset. INPUT: CUST. The page returned 403, so the metrics were not retrieved. — [FLAIRS](https://journals.flvc.org/FLAIRS/article/view/141558)
- **RAILS: Retrieval-Augmented Incremental LLM Clustering at Scale** (arXiv 2609.24464, Sept 2026). INPUT: CUST (support tickets from 4 industries).
  - Method: top-K retrieval from a persistent label pool, batched LLM assignment, and embedding-space label merging.
  - On 6 public benchmarks it improves on the best prior LLM clustering: accuracy 51.2% to 59.3%, NMI 67.2% to 74.8%, ARI 45.4% to 54.7%.
  - It replaced HDBSCAN in a production SaaS ticket-topic-discovery pipeline.
  - Coverage: (a) P, (c) Y.
  - Sources: [arXiv 2609.24464](https://arxiv.org/abs/2609.24464); [HTML](https://arxiv.org/html/2609.24464)
- **Dial-In LLM** (EMNLP 2025 Main). INPUT: CUST.
  - Human-aligned LLM-in-the-loop intent clustering of customer service dialogues.
  - New Chinese dataset: more than 100k real customer-service calls with 1,507 human-annotated clusters.
  - Fine-tuned LLMs agree with humans at more than 95% on semantic evaluation and cluster naming, and the method "significantly outperform[s]" LLM-guided baselines.
  - Source: [arXiv 2412.09049](https://arxiv.org/abs/2412.09049)
- **TopicGPT** (NAACL 2024). Prompt-based topic modelling with natural-language labels. Harmonic-mean purity is 0.74 vs 0.64 for the strongest baseline against human-annotated Wikipedia topics. — [arXiv 2311.01449](https://arxiv.org/abs/2311.01449)
- **LLooM** (CHI 2024). Concept induction that produces high-level concepts with explicit inclusion criteria from unstructured text. — [ACM DL](https://dl.acm.org/doi/10.1145/3613904.3642830); [arXiv 2404.12259](https://arxiv.org/pdf/2404.12259)
- **Comparative study of LDA, BERTopic, TopicGPT and LLooM.** TopicGPT excels at high-precision categorisation. LLooM may diverge from ground-truth labels but shows stronger text-topic relevance. GoalEx is "tailored specifically for clustering". — [Computational Communication Research](https://journal.computationalcommunication.org/article/view/9248)
- **k-LLMmeans** (arXiv 2502.09667, 2025). k-means with LLM-generated summaries as centroids and a mini-batch streaming extension. It "consistently outperforms classical baselines" and approaches LLM-clustering accuracy with a bounded number of LLM calls. The abstract gives no specific numbers. — [arXiv 2502.09667](https://arxiv.org/abs/2502.09667); [GitHub](https://github.com/jairoadiazr/k-LLMmeans)
- **Context-Aware Clustering using LLMs** (arXiv 2405.00988). Another LLM clustering approach. — [arXiv](https://arxiv.org/html/2405.00988v1)
- **Human-in-the-loop evaluation of topic models.** LLMs "struggle to describe the haystack without human help". — [arXiv 2502.14748](https://arxiv.org/pdf/2502.14748)
- **RAG over tickets.**
  - RAG4Tickets (arXiv 2510.08667) does ticket resolution through RAG. — [arXiv 2510.08667](https://arxiv.org/pdf/2510.08667)
  - FRAGATA does hybrid RAG over 20 years of HPC support tickets. — [arXiv 2604.13721](https://arxiv.org/pdf/2604.13721)
  - A 2024 paper applies RAG with knowledge graphs to customer-service question answering. — [arXiv 2404.17723](https://arxiv.org/html/2404.17723v1)
  - All three target resolution or QA, not problem-level RCA.
- **Ticket-BERT** (Liu et al., 2023) labels incident tickets with language models. **Arici et al.** (2023) studies LLM approaches for automatic ticket assignment. Both are cited in TickIt. — [arXiv 2504.08475](https://arxiv.org/html/2504.08475)

### Inferences
- The strongest 2025-2026 comparators for InsightDesk's BERTopic stage are RAILS (production SaaS tickets, incremental) and the FLAIRS ABCD study, which uses the same "LLM normalises the issue, then embed and cluster" idea. InsightDesk could cite them as alternatives to BERTopic.
- No LLM analytics paper found adds per-cluster temporal spike detection or root-cause explanation on top of the clustering. That combination is InsightDesk's differentiator in the literature.

### Gaps
- FLAIRS ABCD numbers, LLooM quantitative results and GoalEx numbers were not retrieved.
- I found no "agentic feedback analysis" paper that combines clustering, surge detection and RCA.

## Benchmarks and datasets for grouping customer complaints into issues or for customer-issue root cause

### Takeaway
Public datasets exist for grouping customer conversations and intents: ABCD (used in the FLAIRS study), the Dial-In LLM Chinese dataset of more than 100k calls with 1,507 clusters, and the six public benchmarks used by RAILS. There is no public benchmark for customer-issue root cause. Every ticket-dedup and RCA evaluation (iPACK, TickIt, LinkCM, RCACopilot, AidAI, WeChat) uses proprietary production data.

### Cited Findings
- ABCD dataset used for LLM-augmented ticket clustering. — [FLAIRS](https://journals.flvc.org/FLAIRS/article/view/141558)
- Dial-In LLM dataset: more than 100k customer-service calls and 1,507 human-annotated clusters. The authors note that "existing English benchmarks lack sufficient semantic diversity and intent coverage". — [arXiv 2412.09049](https://arxiv.org/abs/2412.09049)
- iPACK (3 Azure datasets), TickIt (20,066 ByteDance tickets), the WeChat study (50.3M feedback items) and RCACopilot (Microsoft incidents) all evaluate on internal production data. — [arXiv 2302.09520](https://arxiv.org/abs/2302.09520); [arXiv 2504.08475](https://arxiv.org/html/2504.08475); [arXiv 2508.00593](https://arxiv.org/html/2508.00593); [arXiv 2305.15778](https://arxiv.org/pdf/2305.15778)

### Inferences
- InsightDesk's evaluation will likely need a synthetic or hand-labelled dataset for dedup and RCA, with ABCD or the Dial-In LLM data as a public clustering proxy. This gap in public benchmarks is itself a reportable finding.

### Gaps
- The six RAILS benchmarks were not individually identified. I did not check whether any public dataset pairs customer complaints with ground-truth root causes, and none was found.

## Summary comparison table

| System | Year / venue / org | Input | (a) dedup | (b) sent. | (c) topics | (d) spikes | (e) RCA | (f) HITL/route | Key numbers |
|---|---|---|---|---|---|---|---|---|---|
| iFeedback | 2019 ASE / Tencent | CUST | P | N | P | Y | N | N | not retrieved |
| MID | 2020 FSE / Microsoft | CUST (categorical) | N | N | N | Y | P | N | "significantly outperforms" SOTA |
| LinkCM | 2020 / Microsoft | MIX | P | N | N | N | P | P | 13.1x faster triage |
| DeepTriage | 2020 KDD / Microsoft | incidents | N | N | N | N | N | Y | F1 82.9% |
| iPACK | 2023 ICSE / Microsoft | MIX | Y | N | N | N | P | P | F1 0.871-0.935 |
| Oasis | 2023 FSE-Ind / Microsoft | TELEM | P | N | N | N | P | N | 251x faster than humans |
| RCACopilot | 2024 EuroSys / Microsoft | TELEM | N | N | N | N | Y | P | RCA acc. up to 0.766 |
| X-lifecycle | 2024 FSE-Ind / Microsoft | TELEM+SDLC | N | N | N | N | Y | N | 353 incidents; no numbers in abstract |
| Nissist | 2024 ECAI demo / Microsoft | TSGs | N | N | N | N | P | Y | not stated in abstract |
| TickIt | 2025 arXiv / ByteDance | CUST | Y | N | P | N | P | Y | escalation F1 0.862; dedup F1 0.879; MTTR -39% |
| AidAI | 2025 arXiv / Microsoft | MIX | N | N | N | N | Y | P | Micro-F1 0.854 (secondary source) |
| WeChat study | 2025 arXiv / Tencent | CUST | N | analysed | Y | N | N | N | relevance clf F1 88.71% |
| Dial-In LLM | 2025 EMNLP | CUST | P | N | Y | N | N | Y (human-aligned) | >95% human agreement |
| RAILS | 2026 arXiv | CUST | P | N | Y | N | N | N | ACC 59.3 / NMI 74.8 / ARI 54.7 |
| FLAIRS ABCD | 2026 FLAIRS | CUST | P | N | Y | N | N | N | not retrieved |
| ServiceNow PI | commercial | CUST | Y | N | P | Y (claimed) | N | Y | none published |

Sources for each row are cited in the sections above.
