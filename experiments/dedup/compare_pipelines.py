"""
E2/E3: compare dedup PIPELINES end to end, with thresholds chosen on
issues the evaluation never sees.

Protocol (leave-half-the-issues-out, repeated):
  - split the 32 issue ids into two halves (5 random splits)
  - pick each pipeline's threshold on half A:
      highest pairwise F1 with pairwise precision >= 0.90
  - evaluate on half B only; then swap halves
  - report mean ± sd of pairwise precision / recall / F1, cases,
    contaminated cases and cross-issue assignments on held-out issues

Pipelines:
  v1-online      first-complaint representative, Top-5, STS-B CE >= t
  online-cos     same online loop, decision = cosine(embedding) >= t
  batch-cos      order-free agglomerative clustering (average linkage,
                 cosine) over all complaints, cut at t

  python experiments/dedup/compare_pipelines.py --model BAAI/bge-base-en-v1.5
"""

import argparse
import os
import sys
from itertools import combinations

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist

sys.path.append(os.path.dirname(__file__))

from replay_lab import (  # noqa: E402
    Models, Replay, load_ground_truth,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "results")
SPLIT_SEEDS = [0, 1, 2, 3, 4]
MIN_PRECISION = 0.90


# ==========================================================
# Clusterings -> labels
# ==========================================================

def v1_online(df, emb, models, threshold):
    replay = Replay(df, emb, models, "first", 5, threshold).run()
    return np.array([replay.case_of_row[r] for r in range(len(df))])


def online_cos(emb, threshold, top_k=5):
    reps, labels = [], np.empty(len(emb), dtype=int)
    for i, v in enumerate(emb):
        if reps:
            sims = np.array(reps) @ v
            best = int(np.argmax(sims))  # Top-k is irrelevant for a cosine decision
            if sims[best] >= threshold:
                labels[i] = best
                continue
        reps.append(v)
        labels[i] = len(reps) - 1
    return labels


def per_product(run):
    """Run a clustering separately inside each product (department): one
    company only ever sees its own complaints. Labels are made unique across
    products, so cross-product pairs are never merged."""
    def wrapped(d, e, t):
        labels = np.empty(len(d), dtype=np.int64)
        offset = 0
        groups = d["department"].astype(str).values
        for g in pd.unique(groups):
            rows = np.where(groups == g)[0]
            lab = np.asarray(run(d.iloc[rows].reset_index(drop=True), e[rows], t))
            _, lab = np.unique(lab, return_inverse=True)
            labels[rows] = lab + offset
            offset += lab.max() + 1
        return labels
    return wrapped


def batch_cos(emb, threshold):
    if len(emb) < 2:
        return np.zeros(len(emb), dtype=int)
    tree = linkage(pdist(emb, metric="cosine"), method="average")
    return fcluster(tree, t=1 - threshold, criterion="distance")


# ==========================================================
# Metrics on a subset of complaints
# ==========================================================

def evaluate(labels, issues, rows):
    labels, issues = labels[rows], issues[rows]
    same_case = same_issue = both = 0
    for a, b in combinations(range(len(rows)), 2):
        sc, si = labels[a] == labels[b], issues[a] == issues[b]
        same_case += sc
        same_issue += si
        both += sc and si
    p = both / same_case if same_case else 1.0
    r = both / same_issue if same_issue else 0.0

    contaminated = cross = 0
    for case in np.unique(labels):
        members = issues[labels == case]
        _, counts = np.unique(members, return_counts=True)
        if len(counts) > 1:
            contaminated += 1
            cross += len(members) - counts.max()

    return {
        "pair_precision": p, "pair_recall": r,
        "pair_f1": 2 * p * r / (p + r) if p + r else 0.0,
        "cases": len(np.unique(labels)),
        "contaminated_cases": contaminated,
        "cross_issue_assignments": cross,
    }


def pick_threshold(run, df, emb, rows, grid):
    """Best F1 with precision >= MIN_PRECISION on the given complaint rows."""
    sub_df = df.iloc[rows].reset_index(drop=True)
    sub_emb = emb[rows]
    issues = sub_df["issue_id"].astype(str).values
    best_t, best_f1 = grid[-1], -1.0
    for t in grid:
        m = evaluate(run(sub_df, sub_emb, t), issues, np.arange(len(rows)))
        if m["pair_precision"] >= MIN_PRECISION and m["pair_f1"] > best_f1:
            best_t, best_f1 = t, m["pair_f1"]
    return best_t


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="BAAI/bge-base-en-v1.5")
    parser.add_argument("--prefix", default="")
    parser.add_argument("--strip-templates", action="store_true")
    from normalize import DATA_PATHS
    parser.add_argument("--data", default="synthetic", choices=list(DATA_PATHS))
    parser.add_argument("--per-product", action="store_true",
                        help="cluster each product separately (one company's complaints at a time)")
    parser.add_argument("--pipelines", nargs="+", default=["v1", "online", "batch"],
                        help="subset to run (v1 is slow on long texts)")
    parser.add_argument("--text", default="raw", choices=["raw", "stripped", "boilerplate", "llm", "boilerplate+synonyms", "boilerplate+synonyms_nocode"],
                        help="E4 text normalisation applied before every pipeline")
    args = parser.parse_args()

    from sentence_transformers import SentenceTransformer

    models = Models()                       # MiniLM + STS-B CE for v1
    from normalize import DATA_PATHS
    df = load_ground_truth(path=DATA_PATHS[args.data], strip_templates=args.strip_templates)
    encoder = SentenceTransformer(args.model)
    if args.text != "raw":
        from normalize import apply_text_mode
        df = apply_text_mode(df, args.text, SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"),
                             data=args.data)
    minilm = models.embed(df["cleaned_text"])
    emb = encoder.encode(
        [args.prefix + t for t in df["cleaned_text"]],
        normalize_embeddings=True, show_progress_bar=False,
    )
    issues_all = df["issue_id"].astype(str).values
    issue_ids = np.array(sorted(set(issues_all)))

    pipelines = {
        "v1-online (MiniLM + STS-B CE)": (
            lambda d, e, t: v1_online(d, models.embed(d["cleaned_text"]), models, t),
            np.round(np.arange(0.10, 0.86, 0.05), 3), "minilm",
        ),
        f"online-cos ({args.model})": (
            lambda d, e, t: online_cos(e, t),
            np.round(np.arange(0.30, 0.96, 0.02), 3), "model",
        ),
        f"batch-cos ({args.model})": (
            lambda d, e, t: batch_cos(e, t),
            np.round(np.arange(0.30, 0.96, 0.02), 3), "model",
        ),
    }

    keep = {"v1": "v1-online", "online": "online-cos", "batch": "batch-cos"}
    pipelines = {k: v for k, v in pipelines.items() if any(k.startswith(keep[p]) for p in args.pipelines)}
    if args.per_product:
        pipelines = {k: (per_product(run), grid, which) for k, (run, grid, which) in pipelines.items()}

    rows_out = []
    for seed in SPLIT_SEEDS:
        rng = np.random.default_rng(seed)
        half = set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))
        a = np.where(np.isin(issues_all, list(half)))[0]
        b = np.where(~np.isin(issues_all, list(half)))[0]

        for tune, test in [(a, b), (b, a)]:
            for name, (run, grid, which) in pipelines.items():
                e = minilm if which == "minilm" else emb
                t = pick_threshold(run, df, e, tune, grid)
                test_df = df.iloc[test].reset_index(drop=True)
                labels = run(test_df, e[test], t)
                m = evaluate(labels, test_df["issue_id"].astype(str).values, np.arange(len(test)))
                m.update({"pipeline": name, "split_seed": seed, "threshold": t})
                rows_out.append(m)
                print(f"seed={seed} {name:45s} t={t:.2f} P={m['pair_precision']:.3f} "
                      f"R={m['pair_recall']:.3f} F1={m['pair_f1']:.3f} cases={m['cases']} "
                      f"contam={m['contaminated_cases']} xissue={m['cross_issue_assignments']}", flush=True)

    out = pd.DataFrame(rows_out)
    tag = ("" if args.data == "synthetic" else f"{args.data}_") + args.model.split("/")[-1] + ("_nostock" if args.strip_templates else "")         + ("" if args.text == "raw" else f"_{args.text}") + ("_perproduct" if args.per_product else "")
    out.to_csv(os.path.join(OUT_DIR, f"pipelines_{tag}.csv"), index=False)
    summary = out.groupby("pipeline")[["threshold", "pair_precision", "pair_recall", "pair_f1",
                                       "cases", "contaminated_cases", "cross_issue_assignments"]].agg(["mean", "std"])
    print("\n", summary.round(3).to_string())


if __name__ == "__main__":
    main()
