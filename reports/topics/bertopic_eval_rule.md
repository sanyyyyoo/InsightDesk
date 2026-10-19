# BERTopic topic-quality evaluation: pre-declared rule (2026-10-11, before any run)

What: the app's topic step exactly as deployed (clustering_service._run_bertopic,
"Config 8": all-MiniLM-L6-v2, UMAP n_neighbors 12 / 5 dims / min_dist 0 /
cosine / random_state 42, HDBSCAN min_cluster_size 3 / min_samples 1 / eom,
CountVectorizer 1-2-grams with English + domain stop-words, min_df 2), on
each document's cleaned text (clean_text, as the app's case representative_text).

Data: the 450 team-labelled Play Store reviews (labels/playstore_final_labels.csv).
Reference = the codebook AREA of each review's code (19 areas: Login, Tickets,
Notifications, Stability, ...). Areas are the closest human "topic" labels we
have; they were made for dedup, not for BERTopic, so this is an agreement
measure, not ground truth.

Runs (no tuning, one fixed configuration):
1. per company, as the app runs it (one company database): Zendesk, Freshdesk
   (the two companies with enough reviews; smaller ones listed only);
2. all 450 pooled (diagnostic only).
Metrics: number of topics, outlier share (topic -1), and against areas:
homogeneity (does a topic hold one area?), completeness (is an area kept in one
topic?), V-measure (NMI), ARI; each on all reviews and on non-outliers only.
Department routing (descriptive): for each topic, the department the app's
keyword rules assign (department_service.assign_department), cross-tabulated
with the topics' majority areas.
Reported as is; nothing in the app changes from this run.
