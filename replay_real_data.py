"""
Replay the 1,432-complaint dataset through the REAL app with R1 and the REAL judge.

  - app code: FastAPI /analyze with DEDUP_MODE=r1 (dedup_r1, detector v2, alert
    groups, escalation policy), dashboard endpoints, RCA;
  - Supabase / Pinecone / clock / email: the in-memory stand-ins of
    test_e2e_local.py (nothing reaches the live projects, no email is sent);
  - LLM: gpt-oss-120b on Groq (experiment keys, rotating, waiting on rate
    limits), every answer cached in replay_llm_cache.jsonl, so an interrupted
    replay restarts without repeating calls.
Data: D:/PBL/InsightDesk-dedup/data/master_complaints_v2.csv (944 real Play
Store reviews + 488 synthetic), in date order; every review gets its own user id
(the file has DEFAULT_USER for all real reviews).

Outputs (reports/replay/):
  replay_assignments.csv     complaint -> case, dedup route
  replay_summary.txt         accuracy on the labelled synthetic part, cases,
                             vague summary, spikes, group spikes
  top20_case_review.xlsx     top 20 cases with sample complaints + RCA, for the
                             team's correct / mixed / useless review

  python replay_real_data.py
"""

import hashlib
import json
import os
import sys
import time

os.environ["DEDUP_MODE"] = "r1"
sys.argv = [sys.argv[0]]                       # test_e2e_local must not see --r1 (we patch the LLM ourselves)

import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

import test_e2e_local as env  # noqa: E402   (in-memory Supabase/Pinecone, clock, app client)

if os.getenv("REPLAY_NO_SENTIMENT") == "1":           # grouping-only replays on low-memory machines:
    import backend.services.duplicate_service as _dup  # sentiment never affects grouping, so skipping
    _dup.enrich_case_with_sentiment = lambda *a, **k: None   # it frees the RoBERTa model's memory

EXP = "D:/PBL/InsightDesk-dedup"
DATA = os.getenv("REPLAY_DATA") or os.path.join(EXP, "data", "master_complaints_v2.csv")
TRUTH = os.path.join(EXP, "data", "synthetic_ground_truth.csv")
BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports", "replay")
CACHE = os.getenv("REPLAY_CACHE") or os.path.join(BASE, "replay_llm_cache.jsonl")   # shared unless REPLAY_CACHE (blind runs)
NO_PRODUCT = os.getenv("REPLAY_NO_PRODUCT") == "1"           # fair comparison with the main-branch pipeline
OUT = os.getenv("REPLAY_OUT") or (os.path.join(BASE, "no_product_filter") if NO_PRODUCT else BASE)
MODEL = "openai/gpt-oss-120b"

sys.path.append(os.path.join(EXP, "experiments", "dedup"))


class GroqRotating:
    """JSON calls with the experiment keys: rotate on rate limits, wait as long as Groq says."""

    def __init__(self):
        cwd = os.getcwd()
        os.chdir(EXP)
        os.environ.setdefault("EXPERIMENTS_ALLOW_APP_KEY", "1")
        from normalize import experiment_groq_clients
        self.clients = experiment_groq_clients()
        os.chdir(cwd)
        self.k = 0
        self.free_at = [0.0] * len(self.clients)
        self.cache = {}
        if os.path.exists(CACHE):
            for line in open(CACHE, encoding="utf-8"):
                r = json.loads(line)
                self.cache[r["h"]] = r["reply"]
        self.calls = 0

    def __call__(self, prompt):
        import re
        h = hashlib.sha1(prompt.encode("utf-8")).hexdigest()
        if h in self.cache:
            return self.cache[h]
        while True:
            try:
                resp = self.clients[self.k].chat.completions.create(
                    model=MODEL, temperature=0, response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}])
                reply = json.loads(resp.choices[0].message.content)
                break
            except Exception as exc:
                m = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?([\d.]+)s", str(exc))
                wait = (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + float(m.group(3)) + 5) if m else 30
                now = time.time()
                self.free_at[self.k] = now + wait
                kind = re.findall(r"tokens per (?:day|minute)|requests per (?:day|minute)", str(exc))
                print(f"[groq] key {self.k + 1} limited ({kind[0] if kind else str(exc)[:60]}), wait {wait:.0f}s", flush=True)
                self.k = min(range(len(self.clients)), key=lambda j: self.free_at[j])
                pause = max(0.0, self.free_at[self.k] - now)
                if pause > 0:
                    print(f"[groq] all keys busy, sleeping {pause:.0f}s (next: key {self.k + 1})", flush=True)
                time.sleep(pause)
        self.cache[h] = reply
        self.calls += 1
        with open(CACHE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"h": h, "reply": reply}) + "\n")
        return reply


def pair_scores(cases, issues):
    """Pairwise P/R/F1 over labelled complaints only."""
    df = pd.DataFrame({"c": cases, "i": issues})
    c2 = lambda n: n * (n - 1) / 2
    tp = c2(df.groupby(["c", "i"]).size()).sum()
    pred = c2(df.groupby("c").size()).sum()
    true = c2(df.groupby("i").size()).sum()
    p, r = tp / pred if pred else 0, tp / true if true else 0
    return p, r, 2 * p * r / (p + r) if p + r else 0, int(true)


def main():
    os.makedirs(OUT, exist_ok=True)
    llm = GroqRotating()
    import backend.llm.provider as provider
    provider.generate_json = llm                 # the R1 judge calls go here (dedup_r1.llm_judge)
    if NO_PRODUCT:                               # replay only: R1 searches ALL cases, like the main-branch pipeline
        from backend.services import dedup_r1
        _decide = dedup_r1.decide
        dedup_r1.decide = lambda *a, product=None, **k: _decide(*a, product=None, **k)

    m = pd.read_csv(DATA).reset_index().rename(columns={"index": "row"})
    m["ts"] = pd.to_datetime(m["date"], errors="coerce").fillna(pd.Timestamp("2026-01-01"))
    m = m.sort_values(["ts", "row"]).reset_index(drop=True)
    # spread each day's complaints evenly over the day, in file order
    m["k"] = m.groupby("ts").cumcount()
    m["n"] = m.groupby("ts").row.transform("count")
    m["when"] = m.ts + pd.to_timedelta((m.k + 0.5) / m.n * 24, unit="h")

    out, t0 = [], time.time()
    for idx, r in m.iterrows():
        env.CLOCK[0] = r.when.to_pydatetime().replace(tzinfo=env.timezone.utc)
        res = env.client.post("/analyze", json={
            "complaint_text": str(r.complaint_text)[:5000],   # the API accepts at most 5,000 characters
            "user_id": f"u{int(r.row)}", "rating": None if pd.isna(r.rating) else int(r.rating),
            "source": r.source, "product": r["product"], "is_synthetic": bool(r.is_synthetic)})
        assert res.status_code == 200, res.text
        j = res.json()
        out.append({"row": int(r.row), "when": r.when, "product": r["product"], "is_synthetic": bool(r.is_synthetic),
                    "case_id": j["case_id"], "route": j.get("dedup_route"), "complaint_text": r.complaint_text})
        if (idx + 1) % 50 == 0:
            print(f"{idx + 1}/{len(m)} complaints, {llm.calls} new LLM calls, {time.time() - t0:.0f}s", flush=True)
            pd.DataFrame(out).to_csv(os.path.join(OUT, "replay_assignments.csv"), index=False)
    a = pd.DataFrame(out)
    a.to_csv(os.path.join(OUT, "replay_assignments.csv"), index=False)

    lines = [f"Replay of {len(a)} complaints through the app (DEDUP_MODE=r1, real judge {MODEL})", ""]
    lines.append("dedup routes: " + json.dumps(a.route.value_counts().to_dict()))
    size = a.groupby("case_id").size()
    lines.append(f"cases: {a.case_id.nunique()} | with >= 2 complaints: {int((size >= 2).sum())} | "
                 f"largest: {int(size.max())}")
    truth = pd.read_csv(TRUTH).drop_duplicates("complaint_text").set_index("complaint_text").issue_id
    syn = a[a.is_synthetic].copy()
    syn["issue"] = syn.complaint_text.map(truth)
    syn = syn.dropna(subset=["issue"])
    p, r, f, tr = pair_scores(syn.case_id.values, syn.issue.values)
    lines.append(f"accuracy on the {len(syn)} labelled synthetic complaints ({tr} true pairs): "
                 f"P {p:.3f} R {r:.3f} F1 {f:.3f}")
    mixed = a.groupby("case_id").is_synthetic.nunique()
    lines.append(f"cases mixing real and synthetic complaints: {int((mixed > 1).sum())}")
    by_prod = a.groupby("product").agg(complaints=("row", "size"), cases=("case_id", "nunique"))
    lines.append("\nper product:\n" + by_prod.to_string())

    vs = env.client.get("/dashboard/vague-summary").json()
    lines.append("\nvague summary: " + json.dumps(vs))
    sp = env.client.get("/dashboard/spikes").json()
    gs = env.client.get("/dashboard/group-spikes").json()
    lines.append(f"\nspikes at the end of the replay: {len(sp)} case alerts, {len(gs)} group alerts")
    lines.append("note: spikes are evaluated at each case's latest window; historical review dates make this a"
                 " snapshot, not a live alert stream")

    # top 20 cases for the team's usefulness review, with a real RCA each
    import backend.services.rca_service as rca
    rca.generate_json = llm
    real = a.groupby("case_id").is_synthetic.max() == False   # noqa: E712  cases with no synthetic complaint
    sheets = {"top20_case_review.xlsx": size.sort_values(ascending=False).head(20).index,
              "top20_real_case_review.xlsx": size[real[real].index].sort_values(ascending=False).head(20).index}
    if os.getenv("REPLAY_DATA"):                    # other datasets: one top-20 review sheet
        sheets = {"top20_case_review.xlsx": size.sort_values(ascending=False).head(20).index}
    elif NO_PRODUCT:
        sheets = {}
    elif os.getenv("RCA_NEXT20"):                     # v3 confirmation: real cases ranked 21-40, v1 and v3 RCAs
        nxt = size[real[real].index].sort_values(ascending=False).iloc[20:40].index
        for ver in ("v1", "v3"):
            rca.RCA_PROMPT_VERSION = ver
            write_sheet(f"next20_real_case_review_{ver}.xlsx", nxt, a, rca)
        sheets = {}
    elif os.getenv("RCA_PROMPT_VERSION", "v1").lower() == "v2":         # A/B test: same real cases, v2 RCA
        sheets = {"top20_real_case_review_v2.xlsx": sheets["top20_real_case_review.xlsx"]}
    for sheet, top in sheets.items():
        if not os.path.exists(os.path.join(OUT, sheet)):      # existing review sheets are kept as they are
            write_sheet(sheet, top, a, rca)
    lines.append(f"\nLLM calls made in this run: {llm.calls} (cached answers reused: {len(llm.cache) - llm.calls})")
    open(os.path.join(OUT, "replay_summary.txt"), "w", encoding="utf-8").write("\n".join(lines))
    print("\n".join(lines))


def write_sheet(sheet, top, a, rca):
    """Review sheet: each case's samples + a real RCA, with columns for the team's judgement."""
    rows = []
    for cid in top:
        members = a[a.case_id == cid]
        try:
            rc = rca.generate_rca(int(cid), force_regenerate=True)
            cause = rc.get("probable_cause") if isinstance(rc, dict) else getattr(rc, "probable_cause", "")
            action = rc.get("recommended_action") if isinstance(rc, dict) else getattr(rc, "recommended_action", "")
        except Exception as exc:
            cause, action = f"RCA failed: {exc}", ""
        rows.append({"case_id": int(cid), "complaints": len(members), "products": ", ".join(sorted(set(members["product"]))),
                     "synthetic_share": round(float(members.is_synthetic.mean()), 2),
                     **{f"sample_{k + 1}": t[:300] for k, t in enumerate(members.complaint_text.head(6))},
                     "rca_probable_cause": cause, "rca_recommended_action": action,
                     "same_problem? (correct / mixed / useless)": "", "rca_useful? (yes / partly / no)": "", "notes": ""})
    pd.DataFrame(rows).to_excel(os.path.join(OUT, sheet), index=False)


if __name__ == "__main__":
    main()
