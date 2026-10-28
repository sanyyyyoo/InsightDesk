// Long tables may continue on the next page (header row repeats).
#show figure: set block(breakable: true)

= Results and Discussion

== Introduction

This chapter reports the results of each part of InsightDesk under the protocol of Chapter 6: the grouping step against published methods and general-purpose LLMs, re-joining, generalisation to unseen data, the sensitivity of the thresholds, incident detection, the vague-complaint alarm, sentiment and topics, root-cause explanations, cost and speed, and an end-to-end test. It closes with the limitations of the system.

== Grouping Quality Against Published Methods

@tbl:grouping compares InsightDesk with the baseline methods on the Play Store held-out halves, each baseline at its best-F1 threshold, and gives each method's F1 on Firefox bug reports.

#figure(
  table(
    columns: (4.4cm, 1.6cm, 1.6cm, 1.6cm, 2cm),
    stroke: 0.5pt,
    align: (left + horizon, center + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      table.cell(rowspan: 2)[*Method*], table.cell(colspan: 3)[*Play Store (held-out)*], table.cell(rowspan: 2)[*Firefox F1*],
      [*Precision*], [*Recall*], [*F1*],
    ),
    [*InsightDesk*], [*0.834*], [*0.351*], [*0.494*], [*0.780*],
    [BERTopic topics], [0.158], [0.648], [0.254], [0.541],
    [CLAP (tuned eps)], [0.251], [0.221], [0.235], [0.367],
    [BM25 (REP text model)], [0.306], [0.197], [0.240], [0.472],
    [MinHash-LSH], [0.167], [0.241], [0.197], [0.025],
    [Cross-encoder threshold], [0.377], [0.083], [0.136], [not run],
    [SimHash], [0.072], [0.290], [0.115], [0.039],
    [Single embedding threshold], [0.844], [0.052], [0.098], [0.070],
  ),
  caption: [Pairwise grouping quality of InsightDesk and published methods on identical data],
) <grouping>

#figure(
  image("/content/images/res-f1.png", width: 95%),
  caption: [Pairwise F1 against published methods (Play Store held-out halves; Firefox sample 3)],
) <res-f1>

InsightDesk has the highest F1 of all methods, 0.49 on Play Store with precision 0.83 and recall 0.35, against at most 0.25 for every baseline (@fig:res-f1). Published duplicate finders given the same input and their most favourable threshold reach F1 0.12–0.24. When their threshold is instead chosen to reach precision 0.80 on the tuning half, BM25, MinHash and SimHash recover only 0.8–1.0% of duplicate pairs on the held-out half, while InsightDesk recovers 35% at precision 0.83. Word and character overlap cannot separate different problems that share vocabulary, which is exactly the case the LLM judge exists for.

Topic models group by theme rather than by problem: BERTopic's precision of 0.16 shows how many unrelated complaints share a topic. CLAP's published setting reaches a similar precision to InsightDesk (0.84) but finds only 2% of duplicate pairs. The project's earlier design, a cross-encoder with one threshold, reached precision 0.38; InsightDesk more than doubles it. A single embedding threshold is precise but finds only 5% of duplicates, which confirms that one cut cannot be both safe and inclusive.

#figure(
  image("/content/images/res-pr.png", width: 95%),
  caption: [Pairwise precision and recall of every method, Play Store held-out halves],
) <res-pr>

@fig:res-pr places every method on the precision–recall plane. Every baseline is either precise and finds almost nothing, or finds more and is imprecise; InsightDesk is the only method that keeps precision high while finding a useful share of duplicates.

=== Comparison with general-purpose LLMs

General-purpose LLMs that label each review with the team's codebook group better offline (precision 0.83–0.87, F1 0.64–0.67), but the codebook was written from these same reviews and already names the test problems. When gpt-oss-120b must build its own problem list from earlier reviews of the same companies and then classify new ones, precision falls to 0.62 and F1 to 0.32, below InsightDesk on the same halves (0.81 and 0.39 at the same lower threshold).

A single LLM call that groups a whole batch of one product reaches a similar offline F1 (0.50), but its groups depend on the order of the input: listing the reviews of one held-out half in three shuffled orders kept 78–95% (mean 89%) of its grouped pairs, against 99% for an identical rerun. A batch call also has no memory of earlier batches, so it cannot keep case identifiers, counts or spike histories as complaints arrive. InsightDesk's advantage over a batch LLM is therefore not offline grouping quality but streaming: decisions at arrival time, stable cases, counting and alerting.

== Effect of Case Re-joining

Re-joining recovers duplicates that online decisions split, on short reviews and long bug reports alike (@tbl:rejoin, @fig:res-rejoin).

#figure(
  table(
    columns: (3.2cm, 1fr, 1fr, 2.4cm),
    stroke: 0.5pt,
    align: (left + horizon, center + horizon, center + horizon, center + horizon),
    table.header([*Data*], [*Without re-joining (P / R / F1)*], [*With re-joining (P / R / F1)*], [*Merges correct*]),
    [Play Store], [0.883 / 0.284 / 0.430], [0.834 / 0.351 / 0.494], [23 of 35 (66%)],
    [Firefox sample 3], [0.963 / 0.546 / 0.697], [0.961 / 0.657 / 0.780], [20 of 22 (91%)],
    [Thunderbird], [0.867 / 0.609 / 0.715], [0.873 / 0.721 / 0.790], [17 of 18 (94%)],
  ),
  caption: [Grouping quality before and after one re-joining pass],
) <rejoin>

#figure(
  image("/content/images/res-rejoin.png", width: 90%),
  caption: [Recall with and without one re-joining pass; precision shown below each pair],
) <res-rejoin>

On the Play Store halves re-joining raises recall from 0.284 to 0.351 (+0.067, 95% CI +0.032 to +0.110) and F1 from 0.430 to 0.494 (+0.064, CI +0.025 to +0.112), at a cost in precision from 0.883 to 0.834 (CI −0.139 to +0.002). On bug reports precision is unchanged while recall rises by 11 points. Without re-joining, the grouping step alone reaches precision 0.88 on short reviews; the deployed system trades five points of it for about a quarter more duplicates found. Re-joining is reliable on bug reports (91–94% of merges correct) and noisier on short reviews (66%), where each review gives the judge little to go on.

== Generalisation to Unseen Data

@tbl:generalisation reports results on data that played no part in tuning, with the upper threshold unchanged.

#figure(
  table(
    columns: (3cm, 1fr, 2.2cm, 3.6cm),
    stroke: 0.5pt,
    align: left + horizon,
    table.header([*Setting*], [*Data*], [*Precision*], [*Note*]),
    [Second domain], [Firefox, 3 samples], [0.92–0.96], [F1 0.78 with re-joining (sample 3)],
    [Second domain], [Thunderbird], [0.87], [F1 0.79 with re-joining],
    [Unseen products], [Intercom, Jira SM, ServiceNow], [case 0.92], [No tuning on them],
    [Unseen company], [Leave one company out], [case 0.89], [Thresholds from the other companies],
    [No product field], [889 bug reports, one stream], [0.90], [vs 0.91 with the product],
    [Retrieval at scale], [233,521 bug reports], [RR\@5 0.46–0.56], [BM25 0.40–0.44, REP 0.43–0.44],
    [Third domain], [1,000 Endava tickets], [case 0.90], [Cross-encoder 0.66],
  ),
  caption: [Results on unseen data (upper threshold fixed)],
) <generalisation>

The same upper threshold transfers from short app reviews to long bug reports, and to products and a company never seen in tuning. When every method's threshold is tuned on Play Store reviews and applied unchanged to Firefox reports, InsightDesk's precision rises to 0.96, while surface-similarity methods break down: MinHash-LSH and SimHash merge almost every pair (precision 0.01–0.02) and BM25 falls to precision 0.56. Their scores depend on text length and shared vocabulary, so a cut tuned on short reviews admits nearly all pairs of long reports, whereas InsightDesk's thresholds act on length-insensitive embedding similarity and only settle clear cases. A new deployment can therefore start from the shipped calibration without labelled data in its own format.

Without a product field, treating all Mozilla reports as one stream, precision is 0.90 against 0.91 with the product, so the system does not depend on product metadata. Pairwise precision on unseen help-desk products (0.61–0.64) and on the unseen company (0.59) is lower than on the calibration data, while about 90% of a complaint's case-mates report the same problem; the errors gather in a few large mixed cases. On 1,000 Endava IT tickets, 90% of InsightDesk's cases fall within a single ticket category (case precision 0.904, 95% CI 0.896–0.947), against 0.655 for the earlier cross-encoder pipeline, although it groups far fewer tickets, since category labels are coarser than problems.

== Threshold Calibration and Sensitivity

@tbl:sensitivity shows how precision, recall and the share of complaints sent to the LLM judge change around the calibrated thresholds, measured with live judge calls on the Play Store held-out halves before re-joining, and the two pre-declared confirmations of the short-text lower threshold.

#figure(
  table(
    columns: (4.4cm, 1.8cm, 1.6cm, 1.5cm, 1.5cm, 1.6cm),
    stroke: 0.5pt,
    align: (left + horizon, center + horizon, center + horizon, center + horizon, center + horizon, center + horizon),
    table.header([*Setting*], [*$t_"low"$*], [*Precision*], [*Recall*], [*F1*], [*Judged*]),
    [Calibrated (long-text rule)], [about 0.26], [0.810], [0.259], [0.392], [86%],
    [$t_"low"$ + 0.04], [about 0.30], [0.803], [0.256], [0.388], [81%],
    [$t_"low"$ + 0.09], [about 0.35], [0.867], [0.264], [0.404], [71%],
    [$t_"low"$ + 0.14], [about 0.40], [0.906], [0.260], [0.404], [61%],
    [*Deployed short-text setting*], [*0.40*], [*0.883*], [*0.284*], [*0.430*], [*66%*],
    [Unseen apps: 0.26 → 0.40], [0.26 → 0.40], [0.608 → 0.635], [0.284 → 0.255], [–], [94% → 77%],
    [Bug reports: 0.26 → 0.40], [0.26 → 0.40], [0.908 → 0.912], [0.578 → 0.571], [–], [96% → 90%],
  ),
  caption: [Sensitivity of grouping quality to the lower threshold],
) <sensitivity>

Raising the lower threshold leaves recall essentially unchanged (0.256–0.284) while precision rises and the share of complaints sent to the judge falls from 86% to 61–66%; the 20th-percentile rule is therefore conservative on short reviews. The value 0.40 was confirmed on the 588 reviews of unseen apps under a rule written before the test (judged share down by 17 points, precision up, recall down by less than the allowed 0.03). On bug reports it made almost no difference, because their similarities mostly lie well above 0.40, so 0.26 is kept for long text. For the upper threshold, lowering it by 0.03 or 0.08 keeps precision at 0.81–0.83 and F1 at 0.36–0.41, while lowering it by 0.13 drops precision to 0.72. Only 4% of held-out Play Store complaints reached an automatic join above $t_"high"$, against 86% decided by the judge, so on short reviews the judge does the deciding.

== Incident Detection

Outbreaks were simulated by moving the real reviews of one problem into a short burst inside a 30-day stream of six-hour windows, 300 times per dataset. @tbl:spikes compares the detectors on the same simulated streams; @fig:res-spike summarises the main result.

#figure(
  table(
    columns: (3.4cm, 2.4cm, 1.6cm, 1.8cm, 1.6cm, 1.8cm),
    stroke: 0.5pt,
    align: (left + horizon, left + horizon, center + horizon, center + horizon, center + horizon, center + horizon),
    table.header(
      table.cell(rowspan: 2)[*Detector*], table.cell(rowspan: 2)[*Setting*], table.cell(colspan: 2)[*Play Store*], table.cell(colspan: 2)[*Bug reports*],
      [*Detected*], [*False / 100 w*], [*Detected*], [*False / 100 w*],
    ),
    [*Poisson CUSUM (deployed)*], [*$delta$ = 1, $h$ = 2*], [*42%*], [*0.06*], [*76%*], [*0.38*],
    [Poisson CUSUM], [$delta$ = 1, $h$ = 1.5], [56%], [0.78], [86%], [3.81],
    [Poisson CUSUM], [$delta$ = 1, $h$ = 3], [25%], [0.00], [50%], [0.01],
    [Poisson CUSUM], [$delta$ = 0.5, $h$ = 2], [45%], [0.22], [78%], [1.04],
    [Poisson CUSUM], [$delta$ = 2, $h$ = 2], [33%], [0.02], [67%], [0.10],
    [EWMA chart], [$alpha$ = 0.2, $L$ = 3], [55%], [0.67], [86%], [3.19],
    [Poisson tail test], [count $>= 2$, $p < 0.001$], [43%], [0.27], [71%], [1.20],
    [z-score (feedback tools)], [$z > 2$], [0%], [–], [0%], [–],
  ),
  caption: [Detection of simulated outbreaks per case (false alerts per 100 windows)],
) <spikes>

#figure(
  image("/content/images/res-spike.png", width: 95%),
  caption: [Share of simulated incidents detected; InsightDesk under one false alarm per 100 windows],
) <res-spike>

On unseen Firefox and Thunderbird streams the CUSUM detects 76% of outbreaks per case and 91% per alert group, at 0.38 and 0.69 false alerts per 100 windows. On short Play Store reviews, where an outbreak splits across more cases, it detects 42–43% at 0.06 false alerts. The z-score rule used by commercial feedback tools detects none on the same counts: with zero to two complaints per window, a standard deviation gives no stable baseline.

The standard small-count alternatives were compared on the same simulations. A raw count rule either over-alerts (at least 2 reports: 0.72–4.33 false alerts per 100 windows) or misses most outbreaks (at least 3: 25–49% detected), so a model of the baseline rate is needed. A Poisson tail test on each window detected 71% and 84% on the unseen streams at 1.20 and 1.75 false alerts, about three times the CUSUM's, and an EWMA chart reached 86% on bug reports at 3.2–3.6 false alerts, about nine times the CUSUM's. Across $h in {1, 1.5, 2, 3, 4}$ and $delta in {0.5, 1, 2}$, $h$ = 2 with $delta$ = 1 is the knee: $h$ = 1.5 adds 10 points of detection for ten times the false alarms, and $h$ = 3 loses a third of detections. The setting was chosen on Play Store and a Firefox sample and confirmed unchanged on the unseen streams under a pre-declared rule.

Real complaint counts are burstier than a Poisson model assumes: on 17,236 Firefox reports from two years, per-component variance-to-mean ratios have a median of 1.60 and a pooled value of 2.37 (95% CI 1.70–3.30). Nominal Poisson probabilities therefore understate false alarms (the tail test fires 0.61 times per 100 real windows against 0.10 nominal), which is why all false-alarm rates in this chapter are measured, not computed from the formula.

== Vague-Complaint Alarm

About one review in five is too vague to join any case, so an outage that customers describe only as "the app is not working" is invisible to every per-case detector. @tbl:vague shows the effect of the vague-complaint alarm on 300 simulated vague-only outages per size.

#figure(
  table(
    columns: (5cm, 1fr, 1fr),
    stroke: 0.5pt,
    align: (left + horizon, center + horizon, center + horizon),
    table.header([*Simulated vague-only outage*], [*Per-case detectors*], [*With the vague alarm*]),
    [5 vague complaints], [0%], [52%],
    [10 vague complaints], [0%], [100%],
    [20 vague complaints], [0%], [100%],
    [False alerts per 100 windows], [0.20–0.24], [0.35–0.39],
  ),
  caption: [Detection of outages made only of vague complaints],
) <vague>

The alarm detected every vague-only outage of 10 or more complaints and about half of those with 5, at a cost of about 0.15 extra false alerts per 100 windows. The result held unchanged on the second dataset of unseen help-desk apps, where it detected every 10-complaint outage at 0.19 extra false alerts per 100 windows.

== Sentiment and Topics

@tbl:sentiment compares the two sentiment models evaluated on real Play Store reviews, using star ratings as labels (1–2 stars negative, 3 neutral, 4–5 positive).

#figure(
  table(
    columns: (5cm, 1fr, 1fr, 1fr),
    stroke: 0.5pt,
    align: (left + horizon, center + horizon, center + horizon, center + horizon),
    table.header([*Model*], [*Accuracy*], [*Negative precision*], [*Negative recall*]),
    [*RoBERTa (3 classes, deployed)*], [*0.707*], [*0.81*], [*0.85*],
    [DistilBERT (2 classes)], [0.713], [0.77], [0.95],
  ),
  caption: [Sentiment models against star ratings],
) <sentiment>

DistilBERT reached a slightly higher accuracy but is binary and cannot say neutral, and it is less precise on negative complaints; RoBERTa was therefore chosen. Star ratings are only a proxy for sentiment, since a customer may give a low rating to a neutral description, so these numbers are indicative.

On the 306 cases of the test deployment, BERTopic found 44 topics and left 41 cases (13%) as outliers. Their $c_v$ coherence is 0.49, against 0.38 for random five-word sets from the same texts, so the topics are moderately coherent. The largest are login and sign-in (19 cases), notifications (18), reinstalling or the app not working (16), support plans (15) and email addresses (11). The department rule table routed only 19 of the 44 topics to a named department and sent 25 to General Support, so routing is the weakest step of the pipeline.

== Root-Cause Explanations

The root-cause prompt was improved in two rounds and tested blind: for 20 real cases, two explanations (the original prompt and the new one) were shown in random order to two LLM raters (GPT-6 and Claude), who judged usefulness, unsupported claims and preference. The final prompt was then confirmed on 20 new cases that played no part in writing it. Both raters preferred the final prompt (17:2 and 12:0, the rest ties) and found unsupported claims in fewer cases (12 to 9 and 6 to 2), with no explanation rated not useful.

== Speed and Cost

Measured on 30 live calls with the deployed prompt and five candidates, a judge decision takes 1.34 s at the median (2.09 s at the 90th percentile), uses about 480 input and 270 output tokens, and costs about \$0.00024 at list price, or \$0.24 per 1,000 judged complaints. Embedding a complaint takes 21 ms on a CPU. Because the judge is consulted only inside the band (66% of short reviews at the deployed setting) and at most once per complaint, the cost grows linearly with the number of complaints, not with the number of pairs.

== End-to-End Test

In an end-to-end acceptance test on Firefox reports with re-joining, 32 incidents were injected into otherwise normal streams. 94% of them (30 of 32) became eligible for escalation within 12 hours, and no false alarms occurred on streams without an incident.

== Limitations

- *Recall on short reviews.* Pairwise recall on Play Store is 0.35. Short reviews of one problem often look no more alike than reviews of different problems, and the human annotators themselves agree only at $kappa$ = 0.74. Re-joining, alert groups and the vague-complaint alarm keep incidents visible when a problem is split.
- *Reports, not people.* App-store reviews carry no user identity, so the evaluation counts reports. In the deployed system every complaint carries a verified user, and repeats are not double-counted.
- *Label source.* The Play Store labels were made by the team, and the unseen-product labels by LLM labellers; the Bugzilla results rely on independent links.
- *Deployment without local calibration.* Errors on unseen products gather in a few large mixed cases (pairwise precision 0.59–0.64). Because every escalation requires approval and spikes require a burst of reports, such errors surface as a count or a suggestion a reviewer can reject; for counts trusted without review, a short calibration on a company's own complaints is recommended.
- *A single judge model.* The judge is one open-weight model run at temperature 0; its robustness across models was not measured. A complaint describing two problems can join one case and later attract complaints about the other problem; tracing every join showed this to be a minor source of error.
- *Routing.* The keyword rule table leaves most topics with General Support; a learned or LLM-based mapping is future work.

== Summary

InsightDesk groups complaints with far higher precision than published methods, keeps its calibration on unseen products, companies and text types, detects incidents that the usual z-score misses at under one false alarm per 100 windows, and watches the vague complaints that per-case detectors cannot see. Its main limitation is recall on very short reviews, which the re-joining pass and alert groups partly offset.
