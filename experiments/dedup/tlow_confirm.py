"""t_low 0.40 confirmation on Firefox 3 + Thunderbird (rule: results/tlow_confirm_rule.md)."""
import os, sys
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import e5_three_way as e5
from ci_bootstrap import counts, prf
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress
from replay_lab import load_ground_truth
from sentence_transformers import SentenceTransformer
enc = SentenceTransformer(e5.EMBED_MODEL); e5.MAX_CANDIDATES = 5
res = {}
for data in ("firefox3", "thunderbird"):
    cal = load_ground_truth(path=DATA_PATHS["playstore"]); tgt = load_ground_truth(path=DATA_PATHS[data])
    tgt["complaint_ref"] = tgt["complaint_ref"] + e5.EXT_REF_OFFSET
    cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
    raw = pd.concat([cal[cols].assign(_cal=True), tgt[cols].assign(_cal=False)], ignore_index=True)
    df = apply_text_mode(raw, "boilerplate", enc)
    texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist()); groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values; test = np.where(~df["_cal"].to_numpy(dtype=bool))[0]
    for tl in (0.26, 0.40):
        judge = e5.LLMJudge(texts, refs, f"{data}_ext_playstore", "founder", "gated")
        labels, banded, _ = e5.by_group(lambda r: e5.three_way(emb, r, 0.8306, tl, judge, True), test, groups)
        lab = np.array([f"{groups[i]}|{l}" for i, l in zip(test, labels)]); _, iss = np.unique(issues[test], return_inverse=True)
        c = np.array(counts(lab, iss, np.ones(iss.max() + 1)))
        r = res.setdefault(tl, [np.zeros(3), 0, 0]); r[0] += c; r[1] += banded; r[2] += len(test)
        p, rc, f = prf(*c)[:3]; print(f"{data} t_low {tl}: P {p:.3f} R {rc:.3f} F1 {f:.3f} judged {banded / len(test):.0%}", flush=True)
out = ["T_LOW 0.40 CONFIRMATION (rule results/tlow_confirm_rule.md), Firefox 3 + Thunderbird pooled"]
pr = {}
for tl, (c, b, n) in res.items():
    p, rc, f = prf(*c)[:3]; pr[tl] = (p, rc, b / n)
    out.append(f"  t_low {tl}: P {p:.3f}  R {rc:.3f}  F1 {f:.3f}  judged {b / n:.0%}")
ok = pr[0.40][0] >= pr[0.26][0] - 0.01 and pr[0.40][1] >= pr[0.26][1] - 0.03 and pr[0.26][2] - pr[0.40][2] >= 0.10
out.append("RULE: " + ("ADOPT t_low = 0.40" if ok else "keep t_low = 0.26 (0.40 not confirmed)"))
print("\n".join(out)); open(os.path.join(HERE, "results", "tlow_confirm_results.txt"), "w", encoding="utf-8").write("\n".join(out) + "\n")
