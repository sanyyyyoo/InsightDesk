"""
E7: case representation inside v2 online cosine (founder vs centroid).

Round 1 (replay_lab.py) tested founder / medoid / centroid / multi only in
v1 (STS-B), where cases stay tiny, and found no gain. Krisha's
compare_representation_strategies.py measured retrieval with ideal
leave-one-out issue centroids (98.2% vs 78.3% Top-1). This tests the
realised effect inside v2, where cases grow larger:

  founder         case vector = first complaint (production today; frozen)
  centroid        case vector = running mean of all members (DoorDash-style)
  centroid-safe   running mean updated only by confident merges
                  (similarity >= threshold + 0.05), to limit contamination drift

Same held-out protocol (5 splits x 2, threshold tuned per method on the
tuning half: best F1 with precision >= 0.90), same metrics.

  python experiments/dedup/e7_representation.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))
from compare_pipelines import evaluate, pick_threshold  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
GRID = np.round(np.arange(0.20, 0.96, 0.02), 3)
SAFE_MARGIN = 0.05


def online(emb, t, mode):
    reps, sums, counts = [], [], []
    labels = np.empty(len(emb), dtype=int)
    for i, v in enumerate(emb):
        if reps:
            sims = np.array(reps) @ v
            b = int(np.argmax(sims))
            if sims[b] >= t:
                labels[i] = b
                if mode == "centroid" or (mode == "centroid-safe" and sims[b] >= t + SAFE_MARGIN):
                    sums[b] = sums[b] + v
                    counts[b] += 1
                    reps[b] = sums[b] / np.linalg.norm(sums[b])
                continue
        reps.append(v.copy())
        sums.append(v.copy())
        counts.append(1)
        labels[i] = len(reps) - 1
    return labels


def main():
    from sentence_transformers import SentenceTransformer
    detector = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    configs = [("synthetic", "boilerplate", "sentence-transformers/all-MiniLM-L6-v2"),
               ("synthetic_l1", "boilerplate", "sentence-transformers/all-MiniLM-L6-v2"),
               ("synthetic", "boilerplate+synonyms", "experiments/dedup/models/minilm-simcse"),
               ("synthetic_l1", "boilerplate+synonyms", "experiments/dedup/models/minilm-simcse"),
               ("gitbugs_template", "boilerplate", "sentence-transformers/all-MiniLM-L6-v2")]
    rows = []
    for data, text, model_id in configs:
        df = apply_text_mode(load_ground_truth(path=DATA_PATHS[data]), text, detector, data=data)
        enc = detector if model_id.endswith("all-MiniLM-L6-v2") else SentenceTransformer(model_id)
        emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
        issues = np.array(df["issue_id"].astype(str).tolist())
        ids = np.array(sorted(set(issues)))
        for seed in range(5):
            rng = np.random.default_rng(seed)
            half = set(rng.choice(ids, size=len(ids) // 2, replace=False))
            a, b = np.where(np.isin(issues, list(half)))[0], np.where(~np.isin(issues, list(half)))[0]
            for h, (tune, test) in (("B", (a, b)), ("A", (b, a))):
                for mode in ("founder", "centroid", "centroid-safe"):
                    run = lambda d, e, t, m=mode: online(e, t, m)
                    t = pick_threshold(run, df, emb, tune, GRID)
                    lab = online(emb[test], t, mode)
                    m = evaluate(lab, issues[test], np.arange(len(test)))
                    sizes = np.bincount(lab)
                    m.update({"data": data, "text": text, "model": model_id.split("/")[-1], "mode": mode,
                              "split_seed": seed, "held_out_half": h, "threshold": t,
                              "mean_case_size": float(sizes[sizes > 0].mean())})
                    rows.append(m)
        print(f"done {data} {text} {model_id.split('/')[-1]}", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "e7_representation.csv"), index=False)
    summ = out.groupby(["data", "text", "model", "mode"], sort=False)[
        ["pair_precision", "pair_recall", "pair_f1", "contaminated_cases", "cross_issue_assignments",
         "mean_case_size"]].agg(["mean", "std"]).round(3)
    print(summ.to_string())


if __name__ == "__main__":
    main()
