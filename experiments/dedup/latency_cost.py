"""Latency and cost per judge call with the deployed prompt (30 live calls, experiment keys)."""
import os, sys, time, json, random
import numpy as np, pandas as pd
sys.path.insert(0, "D:/PBL/InsightDesk-claude-review"); sys.path.insert(0, "D:/PBL/InsightDesk-dedup/experiments/dedup")
os.chdir("D:/PBL/InsightDesk-dedup")
from backend.services.dedup_r1 import PROMPT_GATED
from normalize import experiment_groq_clients
from sentence_transformers import SentenceTransformer
d = pd.read_csv("data/external/playstore_scored.csv")
enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
t0 = time.time(); E = enc.encode(d.complaint_text.astype(str).tolist(), normalize_embeddings=True); emb_ms = (time.time() - t0) / len(d) * 1000
clients = experiment_groq_clients(); random.seed(7)
rows = []
for n, i in enumerate(random.sample(range(len(d)), 30)):
    same = np.where(d.department.values == d.department.values[i])[0]; same = same[same != i]
    top = same[np.argsort(-(E[same] @ E[i]))[:5]]
    cases = "\n".join(f"{k + 1}. {d.complaint_text.values[j]}" for k, j in enumerate(top))
    prompt = PROMPT_GATED.format(new=d.complaint_text.values[i], cases=cases)
    for attempt in range(len(clients)):
        c = clients[(n + attempt) % len(clients)]
        try:
            t = time.time()
            r = c.chat.completions.create(model="openai/gpt-oss-120b", temperature=0, response_format={"type": "json_object"},
                                          messages=[{"role": "user", "content": prompt}])
            rows.append((time.time() - t, r.usage.prompt_tokens, r.usage.completion_tokens)); break
        except Exception as e:
            continue
lat = np.array([r[0] for r in rows]); pin = np.array([r[1] for r in rows]); pout = np.array([r[2] for r in rows])
cost = pin * 0.15e-6 + pout * 0.60e-6
out = [f"LATENCY AND COST per judge call (gpt-oss-120b on Groq, deployed prompt, {len(rows)} live calls, 5 candidates each)",
       f"  latency: median {np.median(lat):.2f} s, 90th percentile {np.percentile(lat, 90):.2f} s",
       f"  tokens: input median {int(np.median(pin))}, output median {int(np.median(pout))}",
       f"  cost per call: median ${np.median(cost):.6f}  (= ${np.median(cost) * 1000:.3f} per 1,000 judged complaints; Groq list price $0.15/M in, $0.60/M out)",
       f"  embedding (MiniLM, CPU): {emb_ms:.1f} ms per complaint"]
print("\n".join(out))
open("experiments/dedup/results/latency_cost.txt", "w", encoding="utf-8").write("\n".join(out) + "\n")
