"""Cross-model judge (rule: results/cross_model_rule.md)."""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
os.environ["GROQ_MODEL"] = "llama-3.3-70b-versatile"
import e5_three_way as e5
from ci_bootstrap import counts, prf
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress
from replay_lab import load_ground_truth
from sentence_transformers import SentenceTransformer
enc = SentenceTransformer(e5.EMBED_MODEL); e5.MAX_CANDIDATES = 5
df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
issues = np.array(df["issue_id"].astype(str).tolist()); groups = np.array(df["department"].astype(str).tolist()); refs = df["complaint_ref"].values
ids = np.array(sorted(set(issues))); tot = np.zeros(3)
for seed, half in ((0, "A"), (1, "B"), (1, "A")):
    rng = np.random.default_rng(seed); h = set(rng.choice(ids, size=len(ids) // 2, replace=False))
    a, b = np.where(np.isin(issues, list(h)))[0], np.where(~np.isin(issues, list(h)))[0]
    tune, test = (a, b) if half == "B" else (b, a)
    th, tl = e5.band_thresholds_wide(emb[tune], issues[tune], groups[tune])
    judge = e5.LLMJudge(texts, refs, "playstore_llama", "founder", "gated")
    labels, _, _ = e5.by_group(lambda r: e5.three_way(emb, r, th, tl, judge, True), test, groups)
    lab = np.array([f"{groups[i]}|{l}" for i, l in zip(test, labels)]); _, iss = np.unique(issues[test], return_inverse=True)
    tot += counts(lab, iss, np.ones(iss.max() + 1)); print(f"half {seed}{half} done", flush=True)
p, r, f = prf(*tot)[:3]
out = ["CROSS-MODEL JUDGE (rule results/cross_model_rule.md), Play Store held-out halves pooled",
       "  gpt-oss-120b (deployed): P 0.810 [0.63, 0.96]  R 0.259  F1 0.392",
       f"  llama-3.3-70b-versatile:  P {p:.3f}  R {r:.3f}  F1 {f:.3f}"]
print("\n".join(out)); open(os.path.join(HERE, "results", "cross_model_results.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
