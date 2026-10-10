"""
Q6 (Krisha): one apples-to-apples v1 number on the FULL production dataset.

Offline replay of production case formation on data/master_complaints_v2.csv
(1,432 rows: 944 real Play Store reviews + 488 synthetic), in the same row
order as backend/scripts/ingest_master_csv.py (df.iterrows()), with
production's clean_text, MiniLM retrieval over case founders, Top-5 and the
cross-encoder decision. No Supabase / Pinecone access.

Scored on the 488 labelled synthetic complaints (issue_id joined by exact
text; every text maps to one issue). Real reviews are unlabelled distractors:
they get unique labels, so they never count as correct matches, and merges
between real and synthetic complaints are reported separately.

Configs:
  production   MS-MARCO CE, threshold -2.21  (what built the live 860 cases)
  v1-0.5858    STS-B CE, 0.5858              (f9fcf73 setting)
  v1-0.6469    STS-B CE, 0.6469              (Krisha's contamination-tested choice)
  v2-online    boilerplate removal + online cosine (no LLM), t = 0.44
               (median held-out threshold from E4) and 0.40 / 0.48 sensitivity
Sanity row: STS-B 0.5858 on the 488 synthetic only must reproduce 107 cases,
18 contaminated, 35 cross-issue.

  python experiments/dedup/full_replay.py
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics.cluster import pair_confusion_matrix

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from compare_pipelines import online_cos  # noqa: E402
from normalize import boilerplate_suppress  # noqa: E402
from replay_lab import Models, Replay, case_metrics  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
MASTER = "data/master_complaints_v2.csv"
TRUTH = "data/synthetic_ground_truth.csv"


def load(synthetic_only=False):
    m = pd.read_csv(MASTER)
    truth = pd.read_csv(TRUTH).drop_duplicates("complaint_text").set_index("complaint_text")["issue_id"]
    m["labelled"] = m["is_synthetic"].astype(bool)
    m["issue_id"] = [truth[t] if lab else f"real_{i}" for i, (t, lab) in enumerate(zip(m.complaint_text, m.labelled))]
    if synthetic_only:
        m = m[m.labelled]
    m = m.reset_index(drop=True)
    m["cleaned_text"] = m["complaint_text"].astype(str).map(clean_text)
    return m


def score(df, case_of_row, name):
    labels = np.array([case_of_row[r] for r in range(len(df))])
    lab = df["labelled"].values
    issues = df["issue_id"].astype(str).values
    (tn, fp), (fn, tp) = pair_confusion_matrix(issues[lab], labels[lab]) // 2
    p, r = tp / max(tp + fp, 1), tp / max(tp + fn, 1)
    contaminated = cross = mixed_real = 0
    syn_into_real = 0
    for c in np.unique(labels):
        members = np.where(labels == c)[0]
        syn = members[lab[members]]
        if len(syn):
            _, counts = np.unique(issues[syn], return_counts=True)
            if len(counts) > 1:
                contaminated += 1
                cross += len(syn) - counts.max()
            if (~lab[members]).any():
                mixed_real += 1
                syn_into_real += len(syn) if not lab[members[0]] else 0
    return {"config": name, "complaints": len(df), "cases_total": len(np.unique(labels)),
            "cases_with_synthetic": len(np.unique(labels[lab])),
            "pair_precision": p, "pair_recall": r, "pair_f1": 2 * p * r / (p + r) if p + r else 0.0,
            "TP": int(tp), "FP": int(fp), "FN": int(fn),
            "contaminated_cases": contaminated, "cross_issue_assignments": cross,
            "cases_mixing_real_and_synthetic": mixed_real, "synthetic_in_real_founded_cases": syn_into_real}


def v2_only(modes):
    """E6a: v2 online cosine on the 1,432 set for the given text modes (no v1 replays)."""
    from sentence_transformers import SentenceTransformer
    from normalize import apply_synonyms
    enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    df = load()
    bp = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
    rows = []
    for mode in modes:
        skip = {"verification code"} if mode.endswith("_nocode") else set()
        texts = bp if mode == "boilerplate" else [apply_synonyms(t, skip) for t in bp]
        emb = enc.encode([clean_text(t) for t in texts], normalize_embeddings=True, show_progress_bar=False)
        for t in (0.40, 0.44, 0.48):
            labels = online_cos(emb, t)
            rows.append(score(df, {r: int(c) for r, c in enumerate(labels)}, f"v2 {mode} online cosine {t:.2f}"))
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "full_replay_1432_e6a.csv"), index=False)
    print(out.drop(columns=["TP", "FP", "FN"]).round(3).to_string(index=False))


def main():
    if "--v2-only" in sys.argv:
        return v2_only(["boilerplate", "boilerplate+synonyms", "boilerplate+synonyms_nocode"])
    from sentence_transformers import CrossEncoder, SentenceTransformer
    models = Models()
    stsb = models.cross_encoder
    msmarco = CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")   # Hub id of production's ms-marco-MiniLM-L-6-v2
    rows = []

    # sanity: reproduce the published v1 replay on the 488 synthetic complaints
    syn = load(synthetic_only=True)
    rep = Replay(syn, models.embed(syn["cleaned_text"]), models, "first", 5, 0.5858).run()
    sanity = case_metrics(rep)
    print("sanity (488 synthetic, STS-B 0.5858):", {k: sanity[k] for k in ("final_cases", "contaminated_cases",
                                                                          "cross_issue_assignments")}, flush=True)
    rows.append(score(syn, rep.case_of_row, "sanity: v1 STS-B 0.5858, synthetic only"))

    df = load()
    emb = models.embed(df["cleaned_text"])
    for name, ce, t in (("production: MS-MARCO -2.21", msmarco, -2.21),
                        ("v1: STS-B 0.5858", stsb, 0.5858),
                        ("v1: STS-B 0.6469", stsb, 0.6469)):
        models.cross_encoder, models._ce_cache = ce, {}
        rep = Replay(df, emb, models, "first", 5, t).run()
        rows.append(score(df, rep.case_of_row, name))
        print(rows[-1], flush=True)

    enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    bp = pd.Series(boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)).map(clean_text)
    bp_emb = enc.encode(bp.tolist(), normalize_embeddings=True, show_progress_bar=False)
    for t in (0.40, 0.44, 0.48):
        labels = online_cos(bp_emb, t)
        rows.append(score(df, {r: int(c) for r, c in enumerate(labels)},
                          f"v2 (no LLM): boilerplate + online cosine {t:.2f}"))
        print(rows[-1], flush=True)

    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "full_replay_1432.csv"), index=False)
    print()
    print(out.drop(columns=["TP", "FP", "FN"]).round(3).to_string(index=False))


if __name__ == "__main__":
    main()
