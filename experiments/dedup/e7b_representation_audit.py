"""
E7b: Krisha's follow-ups on case representation.

3c  Real-case laundering test. The 33 real+synthetic mixed cases from the
    v2 full replay (boilerplate + MiniLM online cosine 0.44, 1,432 complaints)
    were hand-judged (results/full_replay_mixed_cases_v2.csv): 12 same problem,
    8 over-broad, 13 wrong merge. Krisha's contamination-safety method: for
    every non-founder member m, similarity of m to its own case represented by
      founder   (first complaint)
      centroid  (mean of all OTHER members, leave-one-out)
      medoid    (the other member with the highest mean cosine to the rest)
    Laundering = the averaged representation makes members of WRONG-merge
    cases look closer to their case than the founder does, i.e. it would
    hide the mistake. Compared by verdict group; members whose source (real /
    synthetic) differs from the founder's are reported separately as the
    likely intruders.

3a+3b  E7 online v2 with a MEDOID mode added, plus rank diagnostics taken
    at decision time for every held-out query whose issue already owns a case
    (majority issue): Top-1/5/10 of the best such case among all cases, and an
    issue-level rank (cases collapsed to their majority issue, so extra
    fragments of the same issue do not add chances).

  python experiments/dedup/e7b_representation_audit.py
"""

import os
import sys
from collections import Counter

import numpy as np
import pandas as pd

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from compare_pipelines import evaluate, online_cos, pick_threshold  # noqa: E402
from full_replay import load  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
GRID = np.round(np.arange(0.20, 0.96, 0.02), 3)


# ------------------------------------------------------------------ 3c
def unit(v):
    return v / max(np.linalg.norm(v), 1e-12)


def laundering(enc):
    df = load()
    bp = [clean_text(t) for t in boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)]
    emb = enc.encode(bp, normalize_embeddings=True, show_progress_bar=False)
    lab = online_cos(emb, 0.44)                      # identical to full_replay v2 at 0.44
    verdict = pd.read_csv(os.path.join(RESULTS, "full_replay_mixed_cases_v2.csv")).set_index("case")["verdict"]
    real = ~df["labelled"].values
    rows = []
    for case, v in verdict.items():
        members = np.where(lab == case)[0]
        founder = members[0]
        for m in members[1:]:
            others = members[members != m]
            cen = unit(emb[others].mean(axis=0))
            if len(others) <= 2:
                med = others[0]
            else:
                s = emb[others] @ emb[others].T
                med = others[int(np.argmax((s.sum(1) - 1) / (len(others) - 1)))]
            rows.append({"case": case, "verdict": v, "member_row": int(m),
                         "cross_source": bool(real[m] != real[founder]),
                         "sim_founder": float(emb[m] @ emb[founder]),
                         "sim_centroid": float(emb[m] @ cen),
                         "sim_medoid": float(emb[m] @ emb[med])})
    r = pd.DataFrame(rows)
    r.to_csv(os.path.join(RESULTS, "e7b_real_case_laundering.csv"), index=False)
    for rep in ("centroid", "medoid"):
        r[f"{rep}_minus_founder"] = r[f"sim_{rep}"] - r["sim_founder"]
        r[f"{rep}_better"] = r[f"sim_{rep}"] > r["sim_founder"]
    print("\n3c  real mixed cases – member similarity to own case (leave-one-out), by hand verdict")
    agg = {"members": ("member_row", "size"), "founder": ("sim_founder", "mean"),
           "centroid": ("sim_centroid", "mean"), "medoid": ("sim_medoid", "mean"),
           "centroid_higher_%": ("centroid_better", "mean"), "medoid_higher_%": ("medoid_better", "mean"),
           "founder_ge_0.44_%": ("sim_founder", lambda x: (x >= 0.44).mean()),
           "centroid_ge_0.44_%": ("sim_centroid", lambda x: (x >= 0.44).mean()),
           "medoid_ge_0.44_%": ("sim_medoid", lambda x: (x >= 0.44).mean())}
    for split, sub in (("all members", r), ("cross-source members (likely intruders)", r[r.cross_source])):
        print(f"  [{split}]")
        print(sub.groupby("verdict").agg(**agg).round(3).to_string())


# ------------------------------------------------------------------ 3a + 3b
def online(emb, t, mode, issues=None, ranks=None):
    reps, members = [], []
    labels = np.empty(len(emb), dtype=int)
    for i, v in enumerate(emb):
        if reps:
            sims = np.array(reps) @ v
            if ranks is not None:
                maj = [Counter(issues[m]).most_common(1)[0][0] for m in members]
                own = [c for c, iss in enumerate(maj) if iss == issues[i]]
                if own:
                    order = np.argsort(-sims)
                    pos = {c: k for k, c in enumerate(order)}
                    case_rank = min(pos[c] for c in own) + 1
                    seen, issue_rank = [], None
                    for c in order:
                        if maj[c] not in seen:
                            seen.append(maj[c])
                            if maj[c] == issues[i]:
                                issue_rank = len(seen)
                                break
                    ranks.append((case_rank, issue_rank))
            b = int(np.argmax(sims))
            if sims[b] >= t:
                labels[i] = b
                members[b].append(i)
                if mode == "centroid":
                    reps[b] = unit(emb[members[b]].mean(axis=0))
                elif mode == "medoid":
                    mm = members[b]
                    if len(mm) >= 3:
                        s = emb[mm] @ emb[mm].T
                        reps[b] = emb[mm[int(np.argmax(s.sum(1)))]]
                continue
        reps.append(v.copy())
        members.append([i])
        labels[i] = len(reps) - 1
    return labels


def e7_medoid_ranks():
    from sentence_transformers import SentenceTransformer
    det = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    configs = [("synthetic", "boilerplate", "sentence-transformers/all-MiniLM-L6-v2"),
               ("synthetic_l1", "boilerplate", "sentence-transformers/all-MiniLM-L6-v2"),
               ("synthetic", "boilerplate+synonyms", "experiments/dedup/models/minilm-simcse"),
               ("synthetic_l1", "boilerplate+synonyms", "experiments/dedup/models/minilm-simcse")]
    rows = []
    for data, text, model_id in configs:
        df = apply_text_mode(load_ground_truth(path=DATA_PATHS[data]), text, det, data=data)
        enc = det if model_id.endswith("L6-v2") else SentenceTransformer(model_id)
        emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
        issues = np.array(df["issue_id"].astype(str).tolist())
        ids = np.array(sorted(set(issues)))
        for seed in range(5):
            rng = np.random.default_rng(seed)
            half = set(rng.choice(ids, size=len(ids) // 2, replace=False))
            a, b = np.where(np.isin(issues, list(half)))[0], np.where(~np.isin(issues, list(half)))[0]
            for h, (tune, test) in (("B", (a, b)), ("A", (b, a))):
                for mode in ("founder", "centroid", "medoid"):
                    t = pick_threshold(lambda d, e, t, m=mode: online(e, t, m), df, emb, tune, GRID)
                    rk = []
                    lab = online(emb[test], t, mode, issues[test], rk)
                    m = evaluate(lab, issues[test], np.arange(len(test)))
                    rk = np.array([(c, i if i is not None else 999) for c, i in rk])
                    m.update({"data": data, "text": text, "model": model_id.split("/")[-1], "mode": mode,
                              "split_seed": seed, "held_out_half": h, "threshold": t, "queries": len(rk),
                              "case_top1": (rk[:, 0] <= 1).mean(), "case_top5": (rk[:, 0] <= 5).mean(),
                              "case_top10": (rk[:, 0] <= 10).mean(),
                              "issue_top1": (rk[:, 1] <= 1).mean(), "issue_top5": (rk[:, 1] <= 5).mean()})
                    rows.append(m)
        print(f"done {data} {text}", flush=True)
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "e7b_medoid_ranks.csv"), index=False)
    cols = ["pair_precision", "pair_recall", "pair_f1", "cross_issue_assignments",
            "case_top1", "case_top5", "case_top10", "issue_top1", "issue_top5"]
    print("\n3a+3b  online v2, 10 held-out runs (means)")
    print(out.groupby(["data", "text", "model", "mode"], sort=False)[cols].mean().round(3).to_string())


if __name__ == "__main__":
    from sentence_transformers import SentenceTransformer
    parts = sys.argv[1:] or ["3c", "3ab"]
    if "3c" in parts:
        laundering(SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"))
    if "3ab" in parts:
        e7_medoid_ranks()
