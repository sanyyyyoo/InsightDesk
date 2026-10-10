"""
Answers to Krisha's review questions (dedup v2 doc), synthetic data only.

  Q2  scorer comparison: same 150 pairs (data/calibration_pairs.csv), same
      protocol for every scorer; also with Krisha's 5 label corrections and
      on raw (uncleaned) text; MS-MARCO added (the model production used).
  Q4  E4 numbers with the identical-core positive pairs excluded from
      scoring (same held-out runs, same saved thresholds).
  Q3  sync_not_updating: which held-out half it falls in per split, and the
      E4 means with that issue removed from the data (thresholds re-tuned).

  python experiments/dedup/krisha_checks.py [q2 q4 q3]
"""

import itertools
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from compare_pipelines import batch_cos, evaluate, online_cos, pick_threshold, v1_online  # noqa: E402
from compare_scorers import recall_at_precision  # noqa: E402
from normalize import apply_text_mode  # noqa: E402
from replay_lab import Models, load_ground_truth, strip_generator_templates  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
SEEDS = [0, 1, 2, 3, 4]
KRISHA_CORRECTIONS = "D:/tmp/ground_truth_corrections.csv"   # upstream 8801740:data/ground_truth_corrections.csv
COS_GRID = np.round(np.arange(0.30, 0.96, 0.02), 3)
V1_GRID = np.round(np.arange(0.10, 0.86, 0.05), 3)


def splits(issue_ids):
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        yield seed, set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))


# ----------------------------------------------------------------- Q2
def q2(models):
    from sentence_transformers import CrossEncoder
    pairs = pd.read_csv("data/calibration_pairs.csv")
    y_orig = (pairs.true_label == "duplicate").astype(int).values
    corr = pd.read_csv(KRISHA_CORRECTIONS)
    y_corr = y_orig.copy()
    y_corr[pairs.pair_id.isin(corr.pair_id).values] = 0
    print(f"\nQ2  150 pairs; positives original {y_orig.sum()}, after Krisha's 5 corrections {y_corr.sum()}", flush=True)

    ce = {"STS-B CE (v1)": models.cross_encoder,
          "Quora CE": CrossEncoder("cross-encoder/quora-distilroberta-base"),
          # production used the legacy id "ms-marco-MiniLM-L-6-v2"; the Hub renamed it to this one
          "MS-MARCO CE (production before f9fcf73)": CrossEncoder("cross-encoder/ms-marco-MiniLM-L6-v2")}
    rows = []
    for text_name, fn in (("cleaned", clean_text), ("raw", str)):
        a, b = pairs.text_a.astype(str).map(fn).tolist(), pairs.text_b.astype(str).map(fn).tolist()
        scores = {"MiniLM cosine": (models.embed(a) * models.embed(b)).sum(1)}
        for name, m in ce.items():
            scores[name] = np.asarray(m.predict(list(zip(a, b)), show_progress_bar=False))
        for name, s in scores.items():
            for lab, y in (("original", y_orig), ("corrected", y_corr)):
                rows.append({"text": text_name, "labels": lab, "scorer": name,
                             "roc_auc": roc_auc_score(y, s), "recall_at_P90": recall_at_precision(y, s, 0.90)})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "krisha_q2_scorers.csv"), index=False)
    print("ROC AUC:")
    print(out.pivot_table(index="scorer", columns=["text", "labels"], values="roc_auc").round(3).to_string())
    print("Recall at precision >= 0.90:")
    print(out.pivot_table(index="scorer", columns=["text", "labels"], values="recall_at_P90").round(3).to_string(),
          flush=True)


# ----------------------------------------------------------------- Q4
def q4(models, encoder, base):
    issues = np.array(base["issue_id"].astype(str).tolist())
    core = np.array(base["complaint_text"].map(strip_generator_templates).tolist())
    issue_ids = np.array(sorted(set(issues)))
    files = {"raw": "pipelines_all-MiniLM-L6-v2.csv", "boilerplate": "pipelines_all-MiniLM-L6-v2_boilerplate.csv",
             "llm": "pipelines_all-MiniLM-L6-v2_llm.csv"}
    rows = []
    for mode, f in files.items():
        d = base if mode == "raw" else apply_text_mode(base, mode, encoder)
        e = encoder.encode(d["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
        saved = pd.read_csv(os.path.join(RESULTS, f))
        for seed, half in splits(issue_ids):
            a = np.where(np.isin(issues, list(half)))[0]
            b = np.where(~np.isin(issues, list(half)))[0]
            for k, (h, test) in enumerate((("B", b), ("A", a))):
                for name, prefix, fn in (("v1", "v1-online", None), ("online", "online-cos", online_cos),
                                         ("batch", "batch-cos", batch_cos)):
                    if name == "v1" and mode != "raw":
                        continue
                    r = saved[(saved.split_seed == seed) & saved.pipeline.str.startswith(prefix)].iloc[k]
                    t = float(r.threshold)
                    if fn is None:
                        td = d.iloc[test].reset_index(drop=True)
                        labels = v1_online(td, models.embed(td["cleaned_text"]), models, t)
                    else:
                        labels = fn(e[test], t)
                    c = {"tp": 0, "fp": 0, "fn": 0, "tp_x": 0, "fn_x": 0, "identical": 0}
                    for i, j in itertools.combinations(range(len(test)), 2):
                        same_case, same_issue = labels[i] == labels[j], issues[test[i]] == issues[test[j]]
                        ident = same_issue and core[test[i]] == core[test[j]]
                        c["identical"] += ident
                        c["tp"] += same_case and same_issue
                        c["fp"] += same_case and not same_issue
                        c["fn"] += same_issue and not same_case
                        c["tp_x"] += same_case and same_issue and not ident
                        c["fn_x"] += same_issue and not same_case and not ident
                    p, rr = c["tp"] / max(c["tp"] + c["fp"], 1), c["tp"] / max(c["tp"] + c["fn"], 1)
                    px, rx = c["tp_x"] / max(c["tp_x"] + c["fp"], 1), c["tp_x"] / max(c["tp_x"] + c["fn_x"], 1)
                    rows.append({"text": mode, "pipeline": name, "split_seed": seed, "held_out_half": h,
                                 "threshold": t, **c, "F1_all": 2 * p * rr / (p + rr) if p + rr else 0,
                                 "saved_F1": float(r.pair_f1), "P_excl": px, "R_excl": rx,
                                 "F1_excl": 2 * px * rx / (px + rx) if px + rx else 0})
    out = pd.DataFrame(rows)
    out.to_csv(os.path.join(RESULTS, "krisha_q4_excl_identical.csv"), index=False)
    print("\nQ4  identical-core positive pairs excluded (same 10 runs, same saved thresholds)")
    print("    sanity: recomputed F1 equals saved F1 in every run:", bool(np.allclose(out.F1_all, out.saved_F1)))
    print(out.groupby(["text", "pipeline"])[["identical", "F1_all", "P_excl", "R_excl", "F1_excl"]]
          .mean().round(3).to_string(), flush=True)


# ----------------------------------------------------------------- Q3
def q3(models, encoder, base):
    issues = np.array(base["issue_id"].astype(str).tolist())
    print("\nQ3  where sync_not_updating falls, and E4 boilerplate online precision per held-out run:")
    saved = pd.read_csv(os.path.join(RESULTS, "pipelines_all-MiniLM-L6-v2_boilerplate.csv"))
    saved = saved[saved.pipeline.str.startswith("online")]
    for seed, half in splits(np.array(sorted(set(issues)))):
        where = "A" if "sync_not_updating" in half else "B"
        p = saved[saved.split_seed == seed].pair_precision.round(3).tolist()
        print(f"    seed {seed}: sync held out in run {seed}-{where} | precision {seed}-B={p[0]} {seed}-A={p[1]}")

    keep = base[base.issue_id != "sync_not_updating"].reset_index(drop=True)
    kissues = np.array(keep["issue_id"].astype(str).tolist())
    emb = {}
    for mode in ("raw", "boilerplate"):
        d = keep if mode == "raw" else apply_text_mode(keep, mode, encoder)
        emb[mode] = (d, encoder.encode(d["cleaned_text"].tolist(), normalize_embeddings=True,
                                       show_progress_bar=False))
    runs = {"v1": (lambda dd, ee, t: v1_online(dd, models.embed(dd["cleaned_text"]), models, t), V1_GRID),
            "online": (lambda dd, ee, t: online_cos(ee, t), COS_GRID),
            "batch": (lambda dd, ee, t: batch_cos(ee, t), COS_GRID)}
    rows = []
    for seed, half in splits(np.array(sorted(set(kissues)))):
        a = np.where(np.isin(kissues, list(half)))[0]
        b = np.where(~np.isin(kissues, list(half)))[0]
        for h, (tune, test) in (("B", (a, b)), ("A", (b, a))):
            for mode, name in (("raw", "v1"), ("raw", "online"), ("boilerplate", "online"), ("boilerplate", "batch")):
                d, e = emb[mode]
                run, grid = runs[name]
                t = pick_threshold(run, d, e, tune, grid)
                td = d.iloc[test].reset_index(drop=True)
                m = evaluate(run(td, e[test], t), kissues[test], np.arange(len(test)))
                m.update({"text": mode, "pipeline": name, "split_seed": seed, "held_out_half": h, "threshold": t})
                rows.append(m)
                print(f"    seed {seed}-{h} {mode:11s} {name:6s} t={t:.2f} P={m['pair_precision']:.3f} "
                      f"R={m['pair_recall']:.3f} F1={m['pair_f1']:.3f}", flush=True)
    res = pd.DataFrame(rows)
    res.to_csv(os.path.join(RESULTS, "krisha_q3_without_sync.csv"), index=False)
    print(f"\n    Without sync_not_updating ({len(keep)} complaints, 31 issues), 10 held-out runs:")
    print(res.groupby(["text", "pipeline"])[["pair_precision", "pair_recall", "pair_f1"]]
          .agg(["mean", "std"]).round(3).to_string(), flush=True)


def main():
    from sentence_transformers import SentenceTransformer
    parts = sys.argv[1:] or ["q2", "q4", "q3"]
    models = Models()
    encoder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    base = load_ground_truth()
    if "q2" in parts:
        q2(models)
    if "q4" in parts:
        q4(models, encoder, base)
    if "q3" in parts:
        q3(models, encoder, base)


if __name__ == "__main__":
    main()
