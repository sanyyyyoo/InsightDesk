= Datasets and Evaluation Protocol

== Introduction

A complaint-grouping system can only be judged against a ground truth that says which complaints report the same problem. This chapter describes the datasets used, where the ground truth of each comes from and how credible it is, the evaluation protocol, the metrics and the baseline methods. The datasets were chosen to be specific to the customer-support domain but not to any one company: the main data cover six help-desk products from six different companies, and further tests use products, a company and text types that played no part in tuning.

== Datasets

@tbl:datasets summarises the datasets.

#figure(
  table(
    columns: (3.4cm, 2cm, 3.2cm, 1fr),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Dataset*], [*Size*], [*Ground truth*], [*Used for*]),
    [Google Play reviews of six help-desk apps (Zendesk, Freshdesk, Help Scout, Zoho Desk, LiveAgent, HappyFox)], [338 scored of 450 labelled], [Three team annotators, written codebook], [Tuning and held-out evaluation],
    [Mozilla Bugzilla: Firefox (three samples) and Thunderbird], [437–479 per sample; 452], [Mozilla triagers' duplicate links], [Transfer to long text],
    [BugHub split: Firefox, Thunderbird, Eclipse], [233,521 reports], [Public duplicate links], [Retrieval at scale (top-5)],
    [Unseen apps: Intercom, Jira Service Management, ServiceNow], [588 reviews], [Agreed key of two LLM labellers], [Transfer to unseen products],
    [Endava IT service tickets], [1,000 tickets], [127 ticket categories], [Third domain (case purity)],
    [Synthetic complaints], [488], [Generator labels], [Component checks only],
  ),
  caption: [Datasets used in the project],
) <datasets>

The Play Store reviews are short: the 338 scored reviews have a median of 21 words (mean 28). Firefox and Thunderbird bug reports are much longer, with a median of 87 and 92 words, which makes them a demanding test of whether thresholds tuned on short reviews transfer to another text type.

== Credibility of the Labels

Each dataset's ground truth comes from a different source, so no single labelling choice drives the results.

=== Play Store: human labels

The three team members labelled the reviews against a written codebook that defines a problem by its user-visible symptom, for example "cannot log in" rather than "login". On a 50-review overlap labelled by all three, a first round reached Fleiss' $kappa$ = 0.57. After the three re-checked the codebook rules they had read differently, agreement rose to $kappa$ = 0.74 (95% confidence interval 0.63–0.84), conventionally read as substantial; remaining disagreements were resolved by discussion, and a blind relabelling round checked consistency. As an external check, three LLMs (gpt-oss, ChatGPT and Claude) given the same codebook agree with the human key at $kappa$ = 0.68–0.70, about as well as the annotators agree with each other, which indicates that the codebook is reproducible rather than idiosyncratic. The labels were fixed before any pipeline variant was scored.

=== Bugzilla: independent labels

Duplicate links in Bugzilla are created by Mozilla's own triagers and developers during normal work: a report is closed as a duplicate and linked to the report it repeats after a person has compared the two. These labels predate this project and were made for engineering rather than research, and the same Bugzilla histories are standard benchmarks for duplicate bug-report detection, including the public BugHub split used here. Because triagers link only the duplicates they notice, some true duplicates are unlinked, and a correct merge of two unlinked duplicates is scored as an error; measured precision on Bugzilla is therefore, if anything, conservative.

=== Unseen products: secondary labels

Labels for the 588 reviews of Intercom, Jira Service Management and ServiceNow are the agreed key of two independent LLM labellers using the same codebook. The two agree only moderately (pairwise $kappa$ = 0.38); the key keeps a pair as a duplicate only when both labellers grouped it, so it is conservative but may still reflect shared LLM biases. These labels are treated as secondary evidence alongside the human and Bugzilla labels.

=== IT tickets and synthetic data

The Endava tickets are real IT service-desk tickets from a third domain, labelled only with one of 127 category codes. A category groups many different problems, so these labels test whether cases are pure, not duplicate detection. The synthetic complaints were used only to check that each component behaves as designed and are not part of any reported comparison.

== Evaluation Protocol

=== Held-out halves

The problems of the Play Store data are split at random into two halves. Thresholds are tuned on one half and the pipeline is scored on the other; three such held-out halves are pooled. Every pipeline change was compared with the current version on identical data under a pass rule written before the run, so that a result could not be explained away after it was seen.

=== Metrics

A grouping is scored over all pairs of complaints of the same product. With TP the number of pairs placed in the same case that report the same problem, FP the pairs placed together that report different problems, and FN the pairs that report the same problem but were placed in different cases:

$ P = "TP" / ("TP" + "FP"), quad R = "TP" / ("TP" + "FN"), quad F_1 = (2 P R) / (P + R) $ <pairwise-metrics>

Pairwise precision answers "of the pairs we put together, how many are truly the same problem"; recall answers "of all true duplicate pairs, how many did we find". *Case precision* is the B-cubed precision: for each complaint, the share of its case that reports the same problem, averaged over complaints. For incident detection, the metrics are the share of simulated outbreaks detected and the number of false alerts per 100 six-hour windows.

Every method has a threshold that trades precision against recall, so neither number alone can rank methods: any method reaches high precision by merging almost nothing, or high recall by merging almost everything. Methods are therefore compared in two ways. First, each baseline's threshold is tuned for its best F1 on the tuning half, the setting most favourable to it. Second, because a wrong merge inflates counts and can trigger a false escalation while a missed duplicate only leaves two smaller cases, recall is also compared at equal precision, with every baseline's threshold set to reach precision 0.80 on the tuning half.

=== Confidence intervals

95% confidence intervals come from a cluster bootstrap over problems, in which pairs between two draws of the same problem are not counted. A simulation with known ground truth confirmed 92–99% coverage for these nominal 95% intervals.

== Baselines

InsightDesk is compared with the methods other systems use for each step, run on identical data and scored with the same metrics:

- *Grouping:* CLAP's density clustering of app reviews @villarroel2016clap; BERTopic topic grouping @grootendorst2022bertopic, the approach behind several commercial feedback tools; BM25 (the text model of REP @sun2011rep), MinHash-LSH @broder1997resemblance and SimHash @manku2007simhash; a single embedding-similarity threshold; a tuned cross-encoder threshold pipeline (the project's earlier design); and general-purpose LLMs used either as labellers or to group a whole batch in one call.
- *Spike detection:* the z-score rule that commercial feedback tools apply per tag or theme, which alerts when a window's count exceeds its mean by more than two standard deviations, applied to the same per-case counts; raw count rules; a per-window Poisson tail test; and an EWMA chart.

Topic models and clustering methods were not designed for problem-level grouping; they are included because commercial tools use them for this purpose. Each method's output is read as a partition, a topic, cluster or case per complaint, and scored pairwise against the same labels, at the better of its published and tuned settings.

== Summary

The evaluation uses human labels with substantial agreement, independent Bugzilla links, unseen products and an unseen company, a third domain, held-out halves, pre-declared pass rules and bootstrap confidence intervals. The next chapter reports the results.
