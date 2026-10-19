# Semantic Duplicate-Detection Methods for Raw Text (Survey Notes)

Context for lessons: the target system embeds customer complaints with MiniLM (bi-encoder), retrieves the top 5 candidates, and re-scores them with an STS-B cross-encoder against a threshold. In internal experiments, plain MiniLM cosine beat the cross-encoder, and batch agglomerative clustering beat online greedy assignment.

## 1. Duplicate question detection (QQP, StackOverflow/AskUbuntu, SemEval CQA): methods, numbers, bi- vs cross-encoder

### Takeaway
Fine-tuned cross-encoders (BERT/RoBERTa) lead pair classification on QQP at about 89-91% accuracy and 72-74 GLUE-F1. Bi-encoders (SBERT) cut large-scale search from hours to seconds while matching cross-encoder quality on in-domain STS. Cross-encoders win clearly only when trained in-domain; out of domain the picture is mixed. The standard design is retrieve-and-rerank, but the reranker has to be trained for the target task.

### Cited Findings
- QQP (GLUE) is binary "are these two Quora questions semantically equivalent?" classification. The classes are unbalanced (63% negative), so both accuracy and F1 are reported, and GLUE averages them — [PMC case study on QQP](https://pmc.ncbi.nlm.nih.gov/articles/PMC11723592/); [BERT paper](https://arxiv.org/pdf/1810.04805)
- GLUE QQP test numbers reported for BERT: base F1 71.2 / acc 89.2; large F1 72.1 / acc 89.3 — [BERT paper](https://arxiv.org/pdf/1810.04805) (as summarized in search results; the GLUE test-server F1 is lower than dev-set F1 figures)
- A fine-tuned bert-base-uncased reached about 91% accuracy and F1 0.8788 on QQP (a model card, not peer reviewed; probably a dev split) — [PromptLayer model card](https://www.promptlayer.com/models/bert-base-uncased-qqp)
- A LoRA-fine-tuned Llama-3.1-70B reached F1 74.4% and accuracy 90.3% on QQP, close to the 8th-ranked leaderboard entry (F1 74.7, acc 90.6). A 70B LLM therefore gives only a marginal gain over BERT-class cross-encoders on this task — [PMC 2025 case study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11723592/)
- SemEval-2016 Task 3 subtask B (question-question similarity, a ranking task): the best system's MAP was 76.70 — [SemEval-2016 Task 3 overview](https://arxiv.org/abs/1912.01972); [task page](https://alt.qcri.org/semeval2016/task3/)
- SBERT (EMNLP 2019) uses siamese/triplet BERT to produce embeddings compared by cosine. Finding the most similar pair in 10,000 sentences drops from about 65 hours with a BERT cross-encoder to about 5 seconds with SBERT, "while maintaining the accuracy from BERT." For Quora's 40M+ questions, answering one query with a cross-encoder would take over 50 hours — [SBERT arXiv](https://arxiv.org/abs/1908.10084); [ar5iv full text](https://ar5iv.labs.arxiv.org/html/1908.10084)
- SBERT STS-B test Spearman: SBERT-NLI-base 77.03 and large 79.23 (no STS-B training); SBERT trained on STS-B: base 84.67, large 84.45; SBERT NLI+STS-B: base 85.35, large 86.10; BERT cross-encoder on STS-B: base 84.30, large 85.64. Baselines: avg GloVe 58.02, BERT CLS vector 16.50. So once fine-tuned in-domain, bi-encoder ≈ cross-encoder on STS-B — [ar5iv SBERT](https://ar5iv.labs.arxiv.org/html/1908.10084)
- The bi-encoder gap widens out of domain. On Argument Facet Similarity with 10-fold CV, SBERT-large scored 77.85 vs BERT cross-encoder 78.68. In cross-topic evaluation it was 53.82 vs 62.02, an 8.2-point gap — [ar5iv SBERT](https://ar5iv.labs.arxiv.org/html/1908.10084)
- Raw BERT CLS/mean embeddings without siamese fine-tuning are poor for similarity (CLS 16.50 on STS-B) — [ar5iv SBERT](https://ar5iv.labs.arxiv.org/html/1908.10084)
- SBERT speed: SBERT-base runs at 1,378 sentences/s on GPU (2,042 with smart batching) and 44-83/s on CPU — [ar5iv SBERT](https://ar5iv.labs.arxiv.org/html/1908.10084)
- Retrieve & rerank guidance from Sentence-Transformers: bi-encoders scale to millions of documents but can return irrelevant candidates. A cross-encoder reranker "can substantially improve the final results" because it attends across both texts, but it is too expensive to run over the whole collection (about 100 candidates is the typical rerank depth). Cross-encoders output a pair score, not an embedding — [SBERT retrieve & rerank docs](https://www.sbert.net/examples/applications/retrieve_rerank/README.html)
- Poly-encoders (Humeau et al., ICLR 2020) sit between the two. On ConvAI2 R@1 they report: bi-encoder 84.8, poly-encoder about 86.8, cross-encoder about 87.9. Cross-encoders are about two orders of magnitude slower at inference — [Poly-encoders arXiv](https://arxiv.org/abs/1905.01969); [summary](https://www.emergentmind.com/topics/poly-encoders)
- For Quora duplicates, Sentence-Transformers recommends two losses. MultipleNegativesRankingLoss, which needs only positive pairs, suits retrieval and duplicate mining but "performs poorly for pair classification." OnlineContrastiveLoss suits classification. Multi-task training with both combines their strengths. Larger batches (350+) help MNRL, and data can be doubled by swapping anchor and positive because duplication is symmetric. The docs give no metric numbers — [SBERT Quora duplicates docs](https://www.sbert.net/examples/sentence_transformer/training/quora_duplicate_questions/README.html)

### Inferences
- An STS-B cross-encoder is trained on graded semantic similarity (0-5) over general-domain news, caption and forum sentences. That objective is not "same underlying problem." Two complaints can share topic and wording (high STS) yet describe different problems, or describe the same problem in different words. The SBERT cross-topic result (8-point swing) shows that pair scorers are sensitive to domain shift. This fits the internal finding that the off-the-shelf STS-B cross-encoder lost to MiniLM cosine: the cross-encoder advantage comes from in-domain training, not from the architecture.
- The SBERT docs' rerank recommendation assumes the reranker is trained for the target relevance notion (for example MS MARCO for search). A reranker trained on a different notion can hurt results. If a reranker is kept, fine-tune it on labeled complaint pairs, or use the bi-encoder alone.
- Top-5 retrieval is shallow compared with the ~100 depth in the rerank guidance. That does not matter if the reranker is removed, but recall@5 of the retriever should be measured before adding any reranking stage.
- Fine-tuning MiniLM with MNRL on in-domain duplicate pairs (mined from resolved cases) is the documented route to better retrieval. OnlineContrastive (or a multi-task mix) gives better-separated scores for threshold decisions.

### Gaps
- I did not locate verified numbers for AskUbuntu (Lei et al. 2016) or the StackOverflow/CQADupStack duplicate benchmarks in this pass.
- No verified QQP number for zero-shot GPT-4-class LLMs. The only LLM figure found is the fine-tuned Llama-3.1-70B result above.

## 2. Duplicate bug report detection: retrieval, Siamese/DL, LLM approaches, metrics

### Takeaway
In duplicate bug report detection (DBRD), the classic IR method REP (BM25F plus feature weighting) matches or beats deep Siamese models on realistic, recent data. The TOSEM 2023 study shows that data-age and issue-tracker biases inflated earlier DL gains. The best LLM results (Cupid) use the LLM to normalize or extract text before retrieval, not to judge pairs directly. Evaluation is ranking-based (Recall Rate@k, MAP).

### Cited Findings
- "Duplicate Bug Report Detection: How Far Are We?" (Zhang, Han, Vinayakarao, Irsan, Xu, Thung, Lo, Jiang; ACM TOSEM 2023):
  - It identifies an age bias (older datasets distort evaluation) and an issue-tracker (Bugzilla/Jira/GitHub) effect.
  - It finds that "a simpler technique outperforms recently proposed sophisticated techniques on most projects."
  - Industrial tools used by Mozilla and VSCode performed comparably to research approaches.
  - Replication package available.
  - Sources: [arXiv 2212.00548](https://arxiv.org/abs/2212.00548); [replication package](https://github.com/soarsmu/TOSEM-DBRD); search summary: IR (REP-based) methods outperformed NN approaches ([arXiv PDF](https://arxiv.org/pdf/2212.00548))
- Cupid (Zhang, Irsan et al., 2023/2024) runs ChatGPT zero-shot to extract "essential information" (keywords) from a bug report and feeds the result into REP. Recall Rate@10 across datasets: 0.602 (Spark), 0.637 (Hadoop), 0.654 (Kibana). Baselines on the same data: REP 0.556 / 0.609 / 0.620; SABD (DL) 0.331 / 0.411 / 0.555; Siamese Pair 0.121 / 0.093 / 0.092. That is a 5-8% gain over REP and up to 82% over the best DL approach — [Cupid arXiv](https://arxiv.org/abs/2308.10022); [Cupid HTML v3](https://arxiv.org/html/2308.10022v3)
- Cupid's cost and design lessons:
  - ChatGPT is applied selectively, only to reports containing dotted identifiers or URLs (about 40-60% of test reports), at about 5 s per report.
  - The authors found that using the LLM to preprocess text beats direct pairwise comparison, on both cost and accuracy.
  - Prompt wording mattered: verbose templates lost about 17%.
  - Llama 3 reached RR@10 comparable to ChatGPT.
  - Source: [Cupid HTML v3](https://arxiv.org/html/2308.10022v3)
- GitBugs (April 2025) has more than 150,000 bug reports from 9 active projects (e.g. Firefox, Cassandra, VS Code) across GitHub, Bugzilla and Jira. It provides predefined train/test splits for duplicate detection, plus per-project duplicate rates, under CC BY 4.0 — [GitBugs arXiv](https://arxiv.org/abs/2504.09651); [GitHub](https://github.com/av9ash/gitbugs)
- GPTrace (ICSE 2026) computes LLM embeddings of stack traces and ASan reports, then clusters them with HDBSCAN to group crashes by root cause. It was evaluated on more than 300,000 crashing inputs with 50 ground-truth bugs across 14 targets and showed "noticeable improvement" over hand-crafted stack-trace similarity and more complex state-of-the-art methods — [GPTrace arXiv](https://arxiv.org/abs/2512.01609); [ICSE 2026 page](https://conf.researchr.org/details/icse-2026/icse-2026-research-track/119/GPTrace-Effective-Crash-Deduplication-Using-LLM-Embeddings)
- A 2025 arXiv paper on DBRD in large open repositories exists but was not reviewed in depth — [arXiv 2504.14797](https://arxiv.org/pdf/2504.14797)

### Inferences
- The DBRD literature matches the internal result. A simpler similarity (REP/BM25F there, MiniLM cosine here) beats a heavier learned pair model when that model is not trained on the target distribution. The Siamese Pair numbers on newer datasets (RR@10 around 0.1) show how badly models can transfer.
- Cupid suggests where to spend LLM budget: normalize each complaint once (extract product, symptom and error keywords into a canonical "problem statement"), then run cheap similarity on the normalized text. This costs O(n) LLM calls instead of O(n·k) pairwise judge calls, and it can be gated to messy or long complaints only.
- GPTrace supports the internal "batch clustering beats online greedy" finding: embed everything, then run density- or hierarchy-based clustering (HDBSCAN or agglomerative) instead of assigning items greedily one at a time.
- To guard against age bias, evaluate on a time-ordered split (train/tune on older complaints, test on newer ones) rather than a random split.

### Gaps
- I did not retrieve verified numbers for DWEN, DC-CNN, HINDBR or SiameseQAT, or for REP's original results (Sun et al. 2011). The TOSEM PDF with per-technique RR@k tables could not be fetched (connection refused), so detailed TOSEM numbers are missing.
- No GitBugs baseline numbers were extracted.

## 3. Entity resolution / record linkage on text: Ditto, DeepMatcher, Magellan, blocking+matching, LLM matching

### Takeaway
The ER pipeline is blocking/candidate generation followed by pairwise matching. Transformer cross-encoder matchers (Ditto) beat DeepMatcher by up to 29% F1. Zero-shot GPT-4 now matches or beats fine-tuned Ditto on 3 of 6 standard benchmarks and is more robust to unseen entities. Prompts must be tuned per dataset, and in-context examples can raise cost by up to 470×.

### Cited Findings
- Ditto (Li et al., VLDB 2021) fine-tunes BERT, DistilBERT or RoBERTa as a sequence-pair classifier. It adds domain-knowledge highlighting, summarization of long strings, and data augmentation with hard examples. It improves F1 by up to 29% over the previous state of the art (DeepMatcher-era). It matches the previous SOTA with at most half the labeled data. On a real company-matching task (789K × 412K records) it reaches 96.5% F1 — [Ditto arXiv](https://arxiv.org/abs/2004.00584)
- Peeters, Steiner & Bizer, "Entity Matching using Large Language Models" (EDBT 2025), GPT-4 zero-shot F1 vs fine-tuned Ditto — [arXiv HTML v4](https://arxiv.org/html/2310.11244v4); [abstract](https://arxiv.org/abs/2310.11244):

  | Dataset | GPT-4 zero-shot F1 | Ditto F1 |
  |---|---|---|
  | WDC Products | 89.61 | 84.90 |
  | Abt-Buy | 95.78 | 91.31 |
  | Walmart-Amazon | 89.67 | 86.39 |
  | Amazon-Google | 76.38 | 80.07 |
  | DBLP-Scholar | 89.82 | 94.31 |
  | DBLP-ACM | 98.41 | 99.00 |

- Other findings from the same paper:
  - The best LLMs need no or few training examples to match PLMs fine-tuned on thousands of examples.
  - LLMs are more robust to unseen entities.
  - "There is no single best prompt"; prompts must be tuned per model and dataset.
  - GPT-4 can generate structured explanations and help diagnose its errors.
  - Fine-tuning GPT-mini or Llama 3.1 gave 1-26% F1 gains.
  - In-context learning and rule-based prompting raised cost 1.5-470× over zero-shot.
  - Source: [arXiv HTML v4](https://arxiv.org/html/2310.11244v4)
- Demonstrations help GPT-4 on some datasets (+9% on Amazon-Google with related demonstrations). On WDC Products and Abt-Buy, GPT-4's performance drops with demonstrations — [Peeters et al. PDF](https://arxiv.org/pdf/2310.11244)
- GPT-4 is reported to outperform the best PLMs by 40-68% F1 in some unseen-entity settings — [Peeters et al. PDF](https://arxiv.org/pdf/2310.11244) (search-result summary; context is the robustness/unseen-entity experiments)
- WDC Products is a multi-dimensional ER benchmark of product offers from thousands of e-shops, built to test seen vs unseen entities and corner cases — [WDC Products arXiv](https://arxiv.org/pdf/2301.09521)
- Small-model alternatives exist: AnyMatch (zero-shot EM with a small LM) and fine-tuned LLMs for EM — [AnyMatch](https://arxiv.org/pdf/2409.04073); [Fine-tuning LLMs for EM](https://arxiv.org/html/2409.08185)

### Inferences
- ER's blocking-then-matching split maps directly onto MiniLM retrieval (blocking) followed by a matcher. The ER literature shows the matcher adds value when it is either trained in-domain (Ditto needs labeled pairs) or strong enough zero-shot to reason about the specific notion of "same entity" (GPT-4). A generic STS cross-encoder is neither.
- If a pair judge is needed for borderline complaint pairs, an LLM judge with a precise "same underlying problem?" definition is the ER-validated zero-shot option. Its prompt still needs tuning on a labeled sample, and it should be applied only to the uncertain band of cosine scores to control cost.

### Gaps
- No verified DeepMatcher or Magellan per-dataset numbers were fetched (only Ditto's "up to 29%" claim). Blocking recall/efficiency numbers were not collected.

## 4. LLM-based dedup: judge, normalization, LLM-guided clustering, cost

### Takeaway
There are three LLM patterns: (a) pairwise judge; (b) per-item normalization or summarization before embedding; (c) LLM-guided clustering (ClusterLLM, k-LLMmeans). The evidence favors (b) and (c) because their cost grows with the number of items or clusters, not the number of pairs. Pairwise judging is accurate (see §3) but its cost scales with candidate pairs.

### Cited Findings
- ClusterLLM (EMNLP 2023) asks ChatGPT hard triplet questions ("does A better correspond to B than C?") to fine-tune a small embedder. It asks pairwise "same cluster?" questions to choose granularity from a hierarchical clustering. It consistently improves clustering across 14 datasets at about $0.6 per dataset and does not need the LLM's embeddings — [ClusterLLM arXiv](https://arxiv.org/abs/2305.14871)
- k-LLMmeans (2025) is k-means in which LLM-generated summaries of clusters periodically replace numeric centroids, which gives human-readable centroids. LLM usage does not grow with dataset size. A k-NLPmeans variant uses cheap deterministic summarizers, and a mini-batch variant handles streaming text — [k-LLMmeans arXiv](https://arxiv.org/abs/2502.09667); [code](https://github.com/jairoadiazr/k-LLMmeans)
- Cupid (see §2): using the LLM to extract essentials before retrieval beat using it for direct comparison, on both cost and accuracy. Selective gating limited LLM calls to 40-60% of items — [Cupid HTML](https://arxiv.org/html/2308.10022v3)
- GPTrace: LLM embeddings plus HDBSCAN clustering for deduplication — [GPTrace](https://arxiv.org/abs/2512.01609)
- LLM entity matching: in-context or rule prompts cost 1.5-470× zero-shot. Prompt sensitivity is high — [Peeters et al.](https://arxiv.org/html/2310.11244v4)

### Inferences
- A good fit for complaint-to-case deduplication:
  1. Optionally normalize each complaint with an LLM into a short canonical problem statement.
  2. Embed with MiniLM, ideally fine-tuned.
  3. Run batch agglomerative clustering or HDBSCAN.
  4. Use an LLM only for (i) the ambiguous similarity band or cluster-merge decisions (ClusterLLM-style pair questions to set granularity) and (ii) case titles or summaries (k-LLMmeans-style centroids).
- ClusterLLM's pairwise granularity questions offer a principled way to choose the agglomerative cut threshold with a few dozen LLM or human labels, instead of hand-tuning a cosine threshold.

### Gaps
- IDAS and TopicGPT were not reviewed in this pass (no verified numbers). No direct head-to-head benchmark was found comparing LLM-judge vs bi-encoder latency and cost on duplicate detection.

## 5. Threshold and score calibration, imbalance, clustering evaluation

### Takeaway
Treat the similarity threshold as an operating point chosen on a labeled, time-held-out sample at a target precision. Calibrate scores if they are used as probabilities (temperature or Platt scaling). Report accuracy together with F1 or PR metrics because duplicates are the minority class. Evaluate clustering with B-cubed P/R, the only standard family that satisfies all of Amigó's formal constraints, alongside pairwise P/R and ARI/NMI.

### Cited Findings
- Modern neural networks are poorly calibrated (typically overconfident). Temperature scaling, a single-parameter Platt scaling fit on held-out data, is "surprisingly effective" and leaves ranking and accuracy unchanged — [Guo et al., ICML 2017](https://proceedings.mlr.press/v70/guo17a.html); [arXiv](https://arxiv.org/abs/1706.04599)
- Imbalance: QQP is 63% negative, so both accuracy and F1 are reported. Real dedup streams are usually far more skewed — [PMC QQP study](https://pmc.ncbi.nlm.nih.gov/articles/PMC11723592/)
- B-cubed precision and recall are computed per item and averaged. They satisfy all four of Amigó et al.'s formal constraints (homogeneity, completeness, rag bag, cluster size vs quantity). Entropy-based measures (MI, V-measure) and the Rand index do not — [Amigó et al. 2009, Information Retrieval 12:461-486](https://www.researchgate.net/publication/225548032_Amigo_E_Gonzalo_J_Artiles_J_et_alA_comparison_of_extrinsic_clustering_evaluation_metrics_based_on_formal_constraints_Inform_Retriev_12461-486); [ACL COLING 2012 usage](https://aclanthology.org/C12-1002.pdf); [python-bcubed](https://github.com/hhromic/python-bcubed)
- DBRD evaluates with ranking metrics (Recall Rate@k, e.g. RR@10), not a single threshold — [Cupid](https://arxiv.org/html/2308.10022v3)
- DBRD evaluation is sensitive to data age and tracker; use realistic, recent test data — [TOSEM 2023](https://arxiv.org/abs/2212.00548)

### Inferences
- The cross-encoder threshold likely failed partly because STS-B scores are calibrated to graded similarity, not duplicate probability. Any score needs a threshold chosen on in-domain labels. Pick it at a precision-oriented point (for example precision ≥ 0.9 on held-out pairs), since wrong merges contaminate cases more than missed merges do. Missed merges can be caught later by periodic re-clustering.
- Cosine scores from MiniLM are not probabilities. Platt or isotonic calibration on labeled pairs makes the threshold interpretable and stable across model updates.
- For clustering-based dedup, report:
  - pairwise precision/recall/F1 (merge correctness)
  - B-cubed P/R/F (per-complaint, robust to cluster-size skew)
  - ARI/NMI as secondary measures
  - retrieval Recall@k for the candidate stage
- Evaluate the batch agglomerative vs online greedy comparison with B-cubed. Greedy online assignment is order-dependent and tends to create fragmented or "rag bag" clusters, which B-cubed penalizes correctly.

### Gaps
- No complaint-domain calibration study was found. Isotonic regression and Platt scaling specifics for similarity thresholds were not separately sourced beyond Guo et al.
