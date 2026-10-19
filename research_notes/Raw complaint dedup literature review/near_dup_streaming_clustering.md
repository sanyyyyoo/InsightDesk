# Near-duplicate detection and streaming/event clustering for raw text

Scope note: these notes come from 18 tool calls. Primary PDFs were read directly (text extracted locally) for Manku et al. 2007, Petrovic et al. 2010, FastStream (arXiv 2101.08595) and SCCL (NAACL 2021). The other sources are abstracts, docs or HTML versions. Numbers appear only where a source was found. Anything else is listed under Gaps.

## 1. Lexical near-duplicates: shingling, MinHash+LSH, SimHash

### Takeaway
Lexical fingerprints (shingles/MinHash, SimHash) work well and scale to billions of documents when the texts are almost identical (templates, boilerplate, counters, timestamps). Accuracy is moderate even there: Google's SimHash at k=3 bits gives precision and recall of about 0.75. They are the wrong tool for grouping differently worded reports of the same problem. For complaints, use them only as a cheap first pass to collapse copy-paste or templated duplicates.

### Cited Findings
- **Manku, Jain, Das Sarma (WWW 2007, Google), "Detecting near-duplicates for web crawling":** shows Charikar's simhash is practical for near-dup detection in a multi-billion-page repository. For 8B pages, 64-bit fingerprints with Hamming distance k = 3 are "reasonable". — [Google Research PDF](https://research.google.com/pubs/archive/33026.pdf); [ACM DL](https://dl.acm.org/doi/10.1145/1242572.1242592)
- Manku et al. tested 2^34 (about 8B) simhash fingerprints, varying k from 1 to 10 and manually tagging sampled pairs as true positive, false positive or unknown. "Choosing k = 3 is reasonable because both precision and recall are near 0.75." A low k misses near-duplicates and a high k produces false positives. — [Google Research PDF](https://research.google.com/pubs/archive/33026.pdf)
- In the Manku et al. labeling guidelines, a true positive is a pair of pages that differ only slightly, "such as only in counters, ads, or timestamps". Radically different pages are false positives. So "near-duplicate" here means almost identical text, not the same meaning. — [Google Research PDF](https://research.google.com/pubs/archive/33026.pdf)
- Scale target in Manku et al.: batch queries of 1M fingerprints against 8B in about 100 seconds, roughly 1B queries per day, using permuted sorted tables on MapReduce. Broder's shingle-based fingerprints need 24 bytes each ("whether two or more Rabin fingerprints out of six are identical"). A 64-bit simhash is much smaller. — [Google Research PDF](https://research.google.com/pubs/archive/33026.pdf)
- **Henzinger (SIGIR 2006), "Finding near-duplicate web pages: a large-scale evaluation of algorithms":** compared Broder shingling with Charikar simhash on 1.6B distinct pages. Neither algorithm works well for near-duplicate pairs on the same site. Both achieve high precision for pairs on different sites. — [Semantic Scholar](https://www.semanticscholar.org/paper/Finding-near-duplicate-web-pages:-a-large-scale-of-Henzinger/5925bc1ca88bf82c3d6d1e798560dec01ee11a16); [ResearchGate](https://www.researchgate.net/publication/221299744_Finding_near-duplicate_web_pages_A_large-scale_evaluation_of_algorithms)
- **FineWeb (HuggingFace, 2024) MinHash configuration for modern LLM pretraining:**
  - Settings: word 5-grams; 112 hash functions in 14 buckets of 8 hashes; target similarity 75%.
  - Detection probability is 77% at 75% similarity, 92% at 80% and 98.8% at 85%. This shows the soft S-curve of LSH banding around the threshold.
  - Source: [FineWeb paper arXiv 2406.17557](https://arxiv.org/html/2406.17557)
- **FineWeb, global vs per-crawl dedup:**
  - Deduplicating globally across 96 Common Crawl snapshots hurt downstream quality. Older snapshots lost 90% of their content, and the data that survived was of lower quality than the data removed.
  - Deduplicating each snapshot independently worked better, giving about 20T tokens.
  - The main gain came from removing "large clusters of duplicates with hundreds of thousands of documents present in all crawls".
  - Source: [arXiv 2406.17557](https://arxiv.org/html/2406.17557)

### Inferences
- Complaint texts about the same issue are usually paraphrases ("app crashes on login" vs "can't sign in, it closes"). They share few 5-gram shingles, so Jaccard/MinHash at a 0.75 threshold would put almost none of them together. Lexical near-dup belongs in a pre-dedup stage for bot, template, form-letter or resubmitted complaints, not in case formation.
- The FineWeb result suggests that dedup being aggressive and "global" can remove the wrong members. For cases, keep all members and only choose a representative. Do not delete near-duplicates, because their volume is the severity signal.
- The Henzinger result (weak on same-site pairs, which share templates) points to a similar risk. Complaints that share a template, such as a support form's boilerplate, may look lexically similar even when the issues differ. Strip boilerplate before fingerprinting.

### Gaps
- Broder 1997 ("On the resemblance and containment of documents") was not fetched in this pass, so no exact shingle size or threshold values are cited from it.
- Henzinger's exact precision numbers for shingles vs simhash were not confirmed from the source text.
- No source was found that quantifies MinHash/SimHash recall on paraphrase datasets. The paraphrase-failure point above is an inference, not a cited result.

## 2. Semantic dedup of large text corpora (SemDeDup, D4, NeMo Curator)

### Takeaway
Embedding-based dedup has a standard recipe:
1. Embed each document.
2. Run k-means to form coarse buckets.
3. Compute pairwise cosine similarity within each bucket.
4. Drop pairs above 1 − ε.

The threshold ε is tuned empirically by looking at the similarity distribution and at downstream effects. It is not derived in a principled way. The k-means pre-bucketing that makes pairwise comparison affordable is structurally the same thing as the "periodic batch clustering" that fixed our fragmentation.

### Cited Findings
- **SemDeDup (Abbas et al., 2023)** uses embeddings from pre-trained models to remove "semantic duplicates: data pairs which are semantically similar, but not exactly identical". It can remove 50% of a LAION subset with minimal performance loss, "effectively halving training time", and improves out-of-distribution performance. On C4 it "improves over prior approaches". — [arXiv 2303.09540](https://arxiv.org/abs/2303.09540)
- SemDeDup setup:
  - Embeddings: CLIP ViT-B/16 for LAION, and the OPT-125M last-layer embedding of the final token for C4.
  - k-means: k = 50,000 clusters for LAION-440M and k = 11,000 for C4.
  - Duplicate rule: cosine similarity ≥ 1 − ε.
  - Source: [arXiv 2303.09540 HTML](https://arxiv.org/html/2303.09540)
- SemDeDup results on LAION:
  - At ε = 0.00095, 30% of images have at least one duplicate. At ε = 0.03, 50% do.
  - Zero-shot ImageNet: 68.74% with 100% of the data, 68.66% with 63%, and 68.27% with 50% (about 2x faster training).
  - Dedup overhead is about 0.91% of the 32-epoch training cost (7h21m for LAION-440M).
  - Source: [arXiv 2303.09540 HTML](https://arxiv.org/html/2303.09540)
- SemDeDup results on C4:
  - About 4% removal matches the NearDup (lexical) baseline.
  - Training on the pruned data reaches single-epoch full-data performance with 10–15% less compute.
  - Larger removals (20%+) raised perplexity in some settings.
  - Source: [arXiv 2303.09540 HTML](https://arxiv.org/html/2303.09540). These numbers come from an automated summary of the HTML and should be verified against the paper's tables.
- **D4 (Tirumala, Simig, Aghajanyan, Morcos, 2023)** selects data with pre-trained model embeddings on top of de-duplicated data. It reports 20% efficiency gains and up to 2% higher average downstream accuracy across 16 NLP tasks at 6.7B parameters. It also finds that "repeating data intelligently consistently outperforms baseline training". — [arXiv 2308.12284](https://arxiv.org/abs/2308.12284)
- **NVIDIA NeMo Curator semantic dedup** follows the same pipeline: embeddings, then k-means, then pairwise cosine similarity within each cluster, then a duplicate threshold.
  - Default embedding model: google/embeddinggemma-300m.
  - Defaults: n_clusters = 100, kmeans_max_iter = 300, eps = 0.01. The quick-start example uses eps = 0.07.
  - Lower eps (e.g., 0.001) is stricter and removes less. Higher eps (0.1) is more aggressive.
  - `which_to_keep` can be "hard" (the default), "easy" or "random".
  - The docs recommend running k-means and the pairwise step with eps=None first, inspecting the similarity distribution, and then choosing eps.
  - Source: [NeMo Curator SemDeDup docs](https://docs.nvidia.com/nemo/curator/curate-text/process-data/deduplication/semdedup); [NeMo Curator workflow API](https://docs.nvidia.com/nemo/curator/nemo-curator/nemo_curator/stages/deduplication/semantic/workflow)
- NeMo Curator gives rough scale and GPU guidance:

  | Documents | GPU memory | Time |
  |---|---|---|
  | <100K | 4–8 GB | 1–2 h |
  | 100K–1M | 8–16 GB | 2–8 h |
  | >1M | >16 GB | 8+ h |

  GPU acceleration is required. — [NeMo Curator docs](https://docs.nvidia.com/nemo/curator/curate-text/process-data/deduplication/semdedup)
- FineWeb itself used only MinHash, and its paper contains no semantic dedup discussion. — [arXiv 2406.17557](https://arxiv.org/html/2406.17557)

### Inferences
- The accepted thresholds are very tight: ε from 0.001 to 0.07 means cosine similarity of about 0.93 to 0.999. At those levels you catch near-paraphrases, not "same underlying problem". Problem-level cases need a much looser threshold, which raises false merges. That calls for a second signal: an entity or product key, a time window, or an LLM or cross-encoder verification step.
- "Inspect the similarity distribution, then choose ε" transfers directly to complaints. Plot the nearest-case similarity for a labeled sample of same-issue vs different-issue pairs and choose the threshold from that plot rather than guessing.
- The two-stage pattern (coarse k-means buckets, then fine pairwise within buckets) mirrors a hybrid online/offline design. Online assignment is cheap, and a periodic batch pass does the more accurate comparisons.

### Gaps
- Dolma's dedup details were not retrieved (it is believed to use Bloom-filter exact/paragraph dedup, which is not verified here).
- No source gives a principled, label-free method for choosing ε. All sources are empirical.

## 3. News/event dedup and first story detection (TDT, Petrovic et al.)

### Takeaway
First story detection (FSD) is the "is this a new case?" decision. The classic TDT approach compares each new document with all previous ones by cosine over TF-IDF (1-NN) and flags it as new if the maximum similarity falls below a threshold. Petrovic et al. showed that LSH makes this constant-time with almost no accuracy loss. They also found that pure LSH nearest-neighbour search gives high-variance decisions, which they fixed by falling back to exact comparison against recent documents. That instability is the same kind of order and approximation sensitivity we see.

### Cited Findings
- **Petrovic, Osborne, Lavrenko (NAACL-HLT 2010), "Streaming First Story Detection with application to Twitter":** an LSH-based FSD algorithm that works in bounded time and space. — [ACL Anthology N10-1021](https://aclanthology.org/N10-1021/)
- The baseline was the UMass FSD system (Allan et al. 2000), a TDT2/TDT3 participant: 1-NN clustering, cosine similarity, TF-IDF with incrementally updated IDF, top 300 features per document. Evaluated on the English part of TDT5 (221,306 documents, April–September 2003). — [ACL PDF](https://aclanthology.org/N10-1021.pdf)
- LSH parameters: k = 13 hyperplanes, with L tables chosen so that the probability of missing a neighbour within distance 0.2 is below 2.5%. — [ACL PDF](https://aclanthology.org/N10-1021.pdf)
- TDT metric: normalized detection cost C_det, which combines miss and false-alarm probabilities. C_min is its minimum over thresholds, and lower is better. The paper also reports DET curves. — [ACL PDF](https://aclanthology.org/N10-1021.pdf)
- **TDT5 results (C_min):**

  | System | C_min |
  |---|---|
  | UMass | 0.69 |
  | Pure LSH | 0.88 (mean of 10 runs, SD 0.046) |
  | LSH + variance reduction | 0.70 (SD 0.004) |
  | Time-bounded LSH | 0.71 |
  | Space- and time-bounded LSH (bucket caps 0.5 / 0.3 / 0.1) | 0.76 / 0.75 / 0.73 |

  UMass took 28 hours versus 2 hours for LSH. UMass time per document grows roughly linearly with the number of documents seen, while LSH stays constant. — [ACL PDF](https://aclanthology.org/N10-1021.pdf)
- The variance-reduction fix: if LSH returns a candidate that is not close enough, the system also compares against a fixed number of the most recent documents ("a backoff towards exact search"). This "greatly improved performance of the system and virtually eliminated variance in the results". — [ACL PDF](https://aclanthology.org/N10-1021.pdf)
- **Twitter results:**
  - Scale: 163.5M timestamped tweets, over 2B tokens.
  - Threads: tweets are linked into threads when similarity is above t = 0.5. Results for t in [0.5, 0.6] were "very much the same".
  - Ranking threads (average precision, Events vs Rest): baseline 16.5, thread size 24.1, unique users 24.5, entropy + users 34.0. Entropy + users also reached 96.3 AP for spam vs rest.
  - Source: [ACL PDF](https://aclanthology.org/N10-1021.pdf)
- Later work: parallel LSH for streaming similarity search over one billion tweets — [PVLDB](https://dl.acm.org/doi/10.14778/2556549.2556574). FSD with word embeddings — [Glasgow eprint](https://eprints.gla.ac.uk/119287/1/119287.pdf).

### Inferences
- The pure-LSH to variance-reduction gap (0.88 to 0.70) shows that approximate nearest-case lookup produces spurious "new case" decisions. If our online assignment uses ANN or compares only against a single representative per case, missed neighbours become fragments. Remedies: an exact backoff over recent complaints and recently active cases, or comparing against several members per case instead of one centroid.
- Petrovic ranked threads by unique users and entropy rather than raw size to separate real events from spam. For complaints, rank or prioritize cases by distinct customers and lexical diversity, which guards against one customer or a bot filing many times.
- The TDT cost-based evaluation (miss vs false alarm with a DET curve) is a good template for tuning our new-case threshold. Fragmentation is a false alarm; over-merging is a miss.

### Gaps
- The original TDT program overview (Allan et al., TDT pilot study) and its official cost weights (C_miss, C_FA, P_target) were not retrieved.
- 2019–2026 Twitter/X event-clustering benchmarks (e.g., Event2012 and Event2018 with SBERT-based streaming) were not covered in this pass.

## 4. Online/streaming short-text clustering

### Takeaway
Most streaming short-text clusterers are single-pass "leader" schemes: assign to the best cluster if its score beats a threshold, else open a new cluster. On top of that they add:
- (a) a model-based or adaptive threshold instead of a fixed one;
- (b) forgetting or deletion of outdated clusters;
- (c) an offline phase that re-clusters or merges micro-clusters (CluStream/DenStream, EStream).

Benchmarks are always averaged over random shuffles because results depend on arrival order. Reported NMI on news-title and tweet streams is about 0.83–0.90. On large, many-cluster StackOverflow streams it drops to about 0.44–0.78.

### Cited Findings
- **FastStream (Rakib & Asaduzzaman, arXiv 2101.08595):**
  - Uses an inverted index over cluster features, so each text is compared only with candidate clusters.
  - Dynamic threshold: compute the max, mean μ and SD σ of the text's similarities to the candidate clusters, and assign to the argmax only if max > μ + σ. Otherwise create a new cluster.
  - Keeps additive cluster-feature (CF) vectors and deletes outdated clusters every DI = 500 texts (tuned on Ns-T).
  - The dynamic threshold is claimed to help with concept drift and avoids per-dataset threshold tuning.
  - Source: [arXiv 2101.08595](https://arxiv.org/pdf/2101.08595)
- FastStream datasets:

  | Dataset | Clusters | Texts | Words/text |
  |---|---|---|---|
  | Ns-T (news titles) | 152 | 11,109 | 6.23 |
  | Ts-T (tweets) | 269 | 30,322 | 7.97 |
  | SO-T (StackOverflow titles) | 10,573 | 123,342 | 5.57 |
  | NTSO-T (combined) | 10,994 | 164,773 | 6.02 |

  Every dataset was randomly shuffled 20 times and NMI averaged, specifically to test random arrival order. — [arXiv 2101.08595](https://arxiv.org/pdf/2101.08595)
- **FastStream NMI (Table 2):**

  | Method | Ns-T | Ts-T | SO-T | NTSO-T |
  |---|---|---|---|---|
  | FastStream-biterm | 0.844 | 0.848 | 0.777 | 0.774 |
  | FastStream-unigram | 0.829 | 0.831 | 0.732 | 0.725 |
  | MStream | 0.859 | 0.867 | 0.618 | 0.608 |
  | MStreamF | 0.879 | 0.877 | 0.652 | 0.619 |
  | DP-BMM | 0.883 | 0.862 | – | – |
  | OSDM | 0.858 | 0.842 | 0.463 | 0.441 |
  | Rakib et al. 2020 (EStream line) | 0.862 | 0.892 | 0.658 | 0.641 |

  The authors attribute the baselines' edge on Ns-T and Ts-T to hyperparameters (α, β) tuned on those datasets. — [arXiv 2101.08595](https://arxiv.org/pdf/2101.08595)
- **FastStream running time (Table 3, seconds):**

  | Method | Ns-T | Ts-T | SO-T | NTSO-T |
  |---|---|---|---|---|
  | FastStream-biterm | 4 | 24 | 101 | 183 |
  | MStream | 227 | 541 | 3319 | 4289 |
  | OSDM | 31 | 196 | 1103 | 1882 |
  | DP-BMM | 5016 | 12307 | – | – |

  Source: [arXiv 2101.08595](https://arxiv.org/pdf/2101.08595)
- **MStream / MStreamF (Yin et al., KDD 2018):** a Dirichlet-process model for short-text streams that handles concept drift and sparsity. MStreamF adds forgetting rules that delete clusters of outdated batches. — [GitHub implementation](https://github.com/danielbis/MStream); [ResearchGate](https://www.researchgate.net/publication/326499341_Model-based_Clustering_of_Short_Text_Streams)
- **EStream (Rakib et al.)** has an online module plus an offline module. It improved clustering quality and running time over the prior stream method. — [Dalhousie thesis/PDF](https://dalspaceb.library.dal.ca/server/api/core/bitstreams/807f8b65-6305-48f8-9e00-c02a943118c3/content); [ResearchGate "Online-Offline Clustering"](https://www.researchgate.net/publication/352413688_Efficient_Clustering_of_Short_Text_Streams_using_Online-Offline_Clustering)
- **OSDM (Online Semantic-enhanced Dirichlet Model)** claims top NMI on News (0.815) and Tweets (0.836) in its own evaluation, per a secondary review. — [Liner review](https://liner.com/review/online-semanticenhanced-dirichlet-model-for-short-text-stream-clustering). This conflicts with FastStream's shuffled evaluation (0.858 / 0.842), which used different dataset variants and protocols. Both come from secondary or competing sources, so treat them with caution.
- **k-LLMmeans / "Summaries as Centroids" (arXiv 2502.09667, ICLR 2026):**
  - Method: k-means in embedding space, but every l iterations each centroid is replaced by the embedding of an LLM summary of up to m k-means++-sampled members. The few-shot variant uses about 10 documents.
  - LLM cost depends only on k and l, not dataset size. A lightweight non-LLM variant, k-NLPmeans, also exists.
  - Mini-batch streaming variant: centroids are updated with weight η = |C*_j| / (|C_j| + |C*_j|).
  - Results (OpenAI embeddings, NMI, k-means → k-LLMmeans-FS5): Bank77 83.0 → 84.1; CLINC 92.0 → 93.1; MASSIVE-Intent 72.4 → 73.9. k-medoids performed worst.
  - Streaming result: mini-batch k-LLMmeans on StackExchange (69,147 posts, 2020–2023) reached 81.6 NMI vs 80.6 for k-means in 2020.
  - Source: [arXiv 2502.09667](https://arxiv.org/abs/2502.09667); [HTML v1](https://arxiv.org/html/2502.09667v1); [OpenReview](https://openreview.net/forum?id=Uzku7RZXvI)

### Inferences
- **Arrival-order sensitivity is expected.** The literature does not remove it; it measures it by averaging over 20 shuffles. We should report our metric as a mean and SD over shuffles too.
- **Fragmentation from a fixed global threshold** is the failure the dynamic μ+σ rule targets. A cheap improvement is to make the new-case decision relative: assign if the best case is clearly above the distribution of similarities to other candidate cases, not merely above an absolute cosine.
- **Our finding that periodic batch agglomerative clustering fixes fragmentation matches the literature's design.** CluStream/DenStream/EStream-style online micro-clusters plus an offline merge phase is the standard answer. Treat online cases as micro-clusters and the batch pass as the macro-clustering or merge step, with stable IDs carried through merges.
- **On case representatives:**
  - A running mean centroid drifts and gets diluted, and in k-LLMmeans tests medoids did worst.
  - A summary-as-centroid (embedding of an LLM-written problem statement, refreshed periodically) gave consistent small NMI gains and produces a human-readable case title. That suits "problem-level" cases.
  - Comparing against several exemplars per case (a multi-prototype approach) is another option.
- **Forgetting and deletion** (MStreamF, FastStream DI = 500) keeps stale cases from attracting new complaints. For complaints, close or archive cases after inactivity instead of deleting them.

### Gaps
- DenStream (Cao et al. 2006) and CluStream (Aggarwal et al. 2003) primary papers were not fetched. Their micro/macro-cluster design is described here from general knowledge and is not cited.
- The OSDM, MStream (KDD 2018) and GSDMM (Yin & Wang, KDD 2014) primary numbers were not verified from the original papers.
- No sources were retrieved on online spherical k-means specifically, or on streaming methods with SBERT embeddings and automatic cluster merging (e.g., 2022–2025 embedding-based stream clustering).

## 5. Short-text clustering benchmarks and SOTA (SCCL, SBERT+clustering)

### Takeaway
On the standard 8 short-text benchmarks, SCCL (contrastive fine-tuning of a Sentence-BERT-style encoder jointly with a clustering loss) raised ACC/NMI substantially over TF-IDF and earlier deep methods. StackOverflow reaches about 75.5 ACC / 74.5 NMI. Biomedical is still hard (about 46 ACC). These are offline, known-k results and serve as upper-bound references for our streaming setup.

### Cited Findings
- **SCCL (Zhang et al., NAACL 2021), "Supporting Clustering with Contrastive Learning":** jointly optimizes instance-level contrastive learning with augmentation (the Contextual Augmenter was best) and a clustering loss. It reports a 3%–11% improvement in accuracy and a 4%–15% improvement in NMI over prior SOTA. Results are averaged over 5 runs. — [ACL Anthology PDF](https://aclanthology.org/2021.naacl-main.427.pdf)
- **SCCL results (ACC / NMI):**

  | Dataset | TF-IDF | HAC-SD | SCCL |
  |---|---|---|---|
  | AgNews | 34.5/11.9 | 81.8/54.6 | 88.2/68.2 |
  | SearchSnippets | 31.5/19.2 | 82.7/63.8 | 85.2/71.1 |
  | StackOverflow | 58.4/58.7 | 64.8/59.5 | 75.5/74.5 |
  | Biomedical | 28.3/23.2 | 40.1/33.5 | 46.2/41.5 |
  | GoogleNews-TS | 68.0/88.9 | 85.8/88.0 | 89.8/94.9 |
  | GoogleNews-T | 58.9/79.3 | 81.8/84.2 | 75.8/88.3 |
  | GoogleNews-S | 61.9/83.0 | 80.6/83.5 | 83.1/90.4 |
  | Tweet | 57.0/80.7 | 89.6/85.2 | 78.2/89.2 |

  Source: [ACL PDF](https://aclanthology.org/2021.naacl-main.427.pdf)
- **SCCL dataset statistics:**

  | Dataset | Docs | Clusters | Avg length (words) | Largest/smallest cluster ratio |
  |---|---|---|---|---|
  | AgNews | 8,000 | 4 | 23 | 1 |
  | StackOverflow | 20,000 | 20 | 8 | 1 |
  | Biomedical | 20,000 | 20 | 13 | 1 |
  | SearchSnippets | 12,340 | 8 | 18 | 7 |
  | GoogleNews-TS / T / S | 11,109 | 152 | 28 / 6 / 22 | 143 |
  | Tweet | 2,472 | 89 | 8 | 249 |

  Source: [ACL PDF](https://aclanthology.org/2021.naacl-main.427.pdf)
- LLM-era intent/short-text clustering benchmarks (Bank77, CLINC, GoEmotions, MASSIVE) with embedding k-means baselines around 72–92 NMI are in the k-LLMmeans paper. — [arXiv 2502.09667v1](https://arxiv.org/html/2502.09667v1)

### Inferences
- GoogleNews and Tweet have many small clusters and heavy imbalance (the largest-to-smallest ratio for Tweet is 249). They resemble complaint streams (a long tail of rare issues plus a few viral ones) better than balanced AgNews or StackOverflow. On these datasets NMI is high but ACC is lower, and SCCL's Tweet ACC (78.2) is below HAC-SD's (89.6). Imbalanced, many-cluster data favours agglomerative/hierarchical methods on ACC, which is consistent with our experience that batch agglomerative fixes fragmentation.
- Domain-adapted contrastive fine-tuning (the SCCL idea) on historical complaints, including pairs from resolved cases as positives, is a plausible way to tighten same-issue similarity before thresholding.

### Gaps
- An exact "SBERT + k-means" baseline row was not present in the SCCL table as extracted. Numbers for that configuration on these datasets were not found in this pass.
- Post-2021 SOTA on these 8 datasets (e.g., RSTC, LLM-guided clustering such as ClusterLLM or IDAS) was not retrieved.
