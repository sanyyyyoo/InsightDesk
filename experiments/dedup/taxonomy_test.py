"""
Auto-generated taxonomy + classification vs R1 (rule: results/taxonomy_rule.md).

  python experiments/dedup/taxonomy_test.py build      # taxonomy per company from history (LLM)
  python experiments/dedup/taxonomy_test.py classify   # classify the 338 test reviews (LLM + embedding)
  python experiments/dedup/taxonomy_test.py score      # compare with R1 on the held-out halves
All LLM outputs are cached in results/taxonomy_test/.
"""

import itertools
import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
from llm_labels import Labeller as _Labeller  # noqa: E402  (gpt-oss-120b with key rotation)


class Labeller(_Labeller):
    """Same key rotation and rate-limit waits, but a reply that is not valid JSON
    (HTTP 400) is retried at most 3 times instead of indefinitely."""

    def _call(self, prompt):
        import time
        bad = 0
        while True:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model, temperature=0, response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}])
                return json.loads(resp.choices[0].message.content)
            except Exception as exc:
                if "Error code: 400" in str(exc) or isinstance(exc, json.JSONDecodeError):
                    bad += 1
                    if bad >= 3:
                        raise RuntimeError("invalid JSON 3 times") from exc
                    continue
                wait = self._next_key(exc)
                if wait > 0:
                    print(f"llm retry in {wait:.0f}s", flush=True)
                    time.sleep(wait)

OUT = os.path.join(HERE, "results", "taxonomy_test")
CHUNK, MAX_CODES, BATCH, EMB_T = 20, 40, 10, 0.50
G = "perproduct_wideband_exemplars_top5"

BUILD = """You are building the list of specific problems that customers report about the {company} customer-support mobile app.

Current list (may be empty):
{current}

New customer reviews:
{reviews}

Update the list so it covers every SPECIFIC problem in the new reviews:
- a problem = one feature + one concrete symptom (e.g. "push notifications for new tickets never arrive", "app logs the user out every time it opens");
- keep existing codes; add a new code only when no existing code is the same problem; do not merge different symptoms;
- reviews with no concrete symptom ("bad app", "doesn't work", praise) do NOT create codes;
- at most {max_codes} codes in total.

Keep each definition under 15 words. Return JSON: {{"problems": [{{"code": "snake_case_code", "definition": "feature + symptom, under 15 words"}}, ...]}} with the FULL updated list."""

CLASSIFY = """Assign each review of the {company} customer-support mobile app to ONE problem from this list.

Problem list (code: definition):
{taxonomy}

Rules:
- pick the code whose definition is the same specific problem (same feature and same symptom) as the review's main complaint;
- "none" if the review names a concrete problem that is not in the list;
- "vague" if the review names no concrete symptom ("bad app", "doesn't work", praise, a rating only).

Reviews:
{reviews}

Return JSON: {{"labels": [{{"id": <review id>, "code": "<code | none | vague>"}}, ...]}} with one entry per review."""


def data():
    test = pd.read_csv(os.path.join(HERE, "..", "..", "data", "external", "playstore_scored.csv"))
    labelled = set(pd.read_csv(os.path.join(HERE, "labels", "playstore_final_labels.csv")).review_text.astype(str))
    m = pd.read_csv(os.path.join(HERE, "..", "..", "data", "master_complaints_v2.csv"))
    norm = lambda x: " ".join(str(x).lower().split())          # compare texts ignoring case and spacing
    excluded = {norm(t) for t in labelled} | {norm(t) for t in test.complaint_text}
    real = m[~m.is_synthetic.astype(bool)]
    hist = real[~real.complaint_text.map(norm).isin(excluded)]
    assert not {norm(t) for t in hist.complaint_text} & {norm(t) for t in test.complaint_text}, "history must not contain test reviews"
    return hist, test


def items(lst, key):
    if isinstance(lst, dict):
        lst = lst.get(key) or next((v for v in lst.values() if isinstance(v, list)), [])
    return [x for x in lst if isinstance(x, dict)]


def build():
    hist, test = data()
    lab = Labeller()
    os.makedirs(OUT, exist_ok=True)
    for company in sorted(test.department.unique()):
        path = os.path.join(OUT, f"taxonomy_{company.replace(' ', '_')}.json")
        if os.path.exists(path):
            continue
        h = hist[hist["product"] == company].complaint_text.astype(str).tolist()
        tax = []
        for k in range(0, len(h), CHUNK):
            reviews = "\n".join(f"- {t[:400]}" for t in h[k:k + CHUNK])
            current = "\n".join(f"{p['code']}: {p['definition']}" for p in tax) or "(empty)"
            try:
                reply = lab._call(BUILD.format(company=company, current=current, reviews=reviews, max_codes=MAX_CODES))
            except Exception as exc:                       # keep the list so far; this chunk is skipped (logged)
                print(f"  {company}: chunk {k // CHUNK + 1} skipped ({str(exc)[:80]})", flush=True)
                continue
            new = items(reply, "problems")
            if new:
                tax = [{"code": str(p.get("code")), "definition": str(p.get("definition"))} for p in new][:MAX_CODES]
        json.dump({"company": company, "history_reviews": len(h), "problems": tax}, open(path, "w"), indent=1)
        print(f"{company}: {len(h)} history reviews -> {len(tax)} problems", flush=True)


def taxonomy(company):
    return json.load(open(os.path.join(OUT, f"taxonomy_{company.replace(' ', '_')}.json")))["problems"]


def classify():
    hist, test = data()
    lab = Labeller()
    path = os.path.join(OUT, "classified_llm.jsonl")
    done = {json.loads(l)["complaint_ref"] for l in open(path)} if os.path.exists(path) else set()
    for company, g in test.groupby("department"):
        tax = taxonomy(company)
        codes = {p["code"] for p in tax}
        listing = "\n".join(f"{p['code']}: {p['definition']}" for p in tax)
        g = g[~g.complaint_ref.isin(done)]
        for k in range(0, len(g), BATCH):
            chunk = g.iloc[k:k + BATCH]
            reviews = "\n".join(f'id {r.complaint_ref}: "{r.complaint_text}"' for r in chunk.itertuples())
            reply = lab._call(CLASSIFY.format(company=company, taxonomy=listing, reviews=reviews))
            got = {int(x["id"]): str(x.get("code")) for x in items(reply, "labels") if str(x.get("id", "")).isdigit()}
            with open(path, "a") as f:
                for r in chunk.itertuples():
                    if r.complaint_ref in got:
                        c = got[r.complaint_ref]
                        f.write(json.dumps({"complaint_ref": int(r.complaint_ref), "company": company,
                                            "code": c if c in codes or c in ("none", "vague") else "none"}) + "\n")
        print(f"{company}: classified", flush=True)
    # no-LLM variant: nearest definition
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    rows = []
    for company, g in test.groupby("department"):
        tax = taxonomy(company)
        if not tax:
            rows += [{"complaint_ref": int(r), "code": "none"} for r in g.complaint_ref]
            continue
        de = enc.encode([p["definition"] for p in tax], normalize_embeddings=True)
        te = enc.encode(g.complaint_text.astype(str).tolist(), normalize_embeddings=True)
        s = te @ de.T
        for r, i, v in zip(g.complaint_ref, s.argmax(1), s.max(1)):
            rows.append({"complaint_ref": int(r), "code": tax[i]["code"] if v >= EMB_T else "none"})
    pd.DataFrame(rows).to_csv(os.path.join(OUT, "classified_emb.csv"), index=False)
    print("embedding variant done")


def score():
    hist, test = data()
    t = test.set_index("complaint_ref")
    llm = pd.DataFrame([json.loads(l) for l in open(os.path.join(OUT, "classified_llm.jsonl"))]) \
        .drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").code
    emb = pd.read_csv(os.path.join(OUT, "classified_emb.csv")).set_index("complaint_ref").code
    print("LLM classification:", llm.value_counts().pipe(lambda v: {"none": int(v.get("none", 0)), "vague": int(v.get("vague", 0)),
                                                                     "coded": int(len(llm) - v.get("none", 0) - v.get("vague", 0))}))
    R = os.path.join(HERE, "results")

    def load(f, seed, half):
        a = pd.read_csv(os.path.join(R, f + ".csv"))
        a = a[(a.judge == "llm") & (a.split_seed.astype(str) == str(seed)) & (a.held_out_half == half)]
        return a.drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").case
    parts = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", 0, "A"),
             load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", 1, "A"),
             load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", 1, "B")]

    def same_code(code, x, y):
        cx, cy = code.get(x, "none"), code.get(y, "none")
        return cx == cy and cx not in ("none", "vague") and t.at[x, "department"] == t.at[y, "department"]

    methods = {
        "R1 (open dedup)": lambda a, x, y: a[x] == a[y],
        "T-LLM (auto taxonomy, LLM classify)": lambda a, x, y: same_code(llm, x, y),
        "T+R1 hybrid (approx.)": lambda a, x, y: (same_code(llm, x, y) or
                                                  (llm.get(x) == "none" and llm.get(y) == "none" and a[x] == a[y])),
        "T-emb (auto taxonomy, no-LLM classify)": lambda a, x, y: same_code(emb, x, y),
    }
    pairs = [(a, x, y) for a in parts for x, y in itertools.combinations(a.index, 2)]
    truth = np.array([t.at[x, "issue_id"] == t.at[y, "issue_id"] for _, x, y in pairs])
    issue_of_pair = np.array([t.at[x, "issue_id"] for _, x, y in pairs])
    pred = {k: np.array([f(a, x, y) for a, x, y in pairs]) for k, f in methods.items()}
    # cluster bootstrap over issues (corrected weighting, see ci_bootstrap.counts)
    issues = sorted(set(t.issue_id))
    pos = {i: n for n, i in enumerate(issues)}
    ix = np.array([pos[t.at[x, "issue_id"]] for _, x, y in pairs])
    iy = np.array([pos[t.at[y, "issue_id"]] for _, x, y in pairs])
    rng = np.random.default_rng(11)

    def prf(p, w):
        tp = (w * (p & truth)).sum(); pp = (w * p).sum(); tt = (w * truth).sum()
        P = tp / pp if pp else 0; Rr = tp / tt if tt else 0
        return np.array([P, Rr, 2 * P * Rr / (P + Rr) if P + Rr else 0])
    ones = np.ones(len(pairs))
    boot = {k: [] for k in pred}
    for _ in range(2000):
        cw = np.bincount(rng.integers(0, len(issues), len(issues)), minlength=len(issues)).astype(float)
        w = np.where(ix == iy, cw[ix], cw[ix] * cw[iy])     # corrected: same-issue pairs once per copy
        for k, p in pred.items():
            boot[k].append(prf(p, w))
    print(f"\nheld-out halves s0A, s1A, s1B pooled: {len(pairs)} pairs, {int(truth.sum())} true duplicate pairs")
    base = np.array(boot["R1 (open dedup)"])
    for k, p in pred.items():
        pt = prf(p, ones)
        lo, hi = np.percentile(np.array(boot[k]), [2.5, 97.5], axis=0)
        line = f"  {k:40s} P {pt[0]:.3f} [{lo[0]:.3f},{hi[0]:.3f}]  R {pt[1]:.3f}  F1 {pt[2]:.3f} [{lo[2]:.3f},{hi[2]:.3f}]"
        if k != "R1 (open dedup)":
            d = np.array(boot[k]) - base
            line += f" | F1 vs R1 {pt[2] - prf(pred['R1 (open dedup)'], ones)[2]:+.3f}, ahead in {(d[:, 2] > 0).mean():.0%}"
        print(line)
    r1 = prf(pred["R1 (open dedup)"], ones)
    t_ = prf(pred["T-LLM (auto taxonomy, LLM classify)"], ones)
    print("\nRULE: T-LLM better than R1" if (t_[0] >= 0.80 and t_[2] >= r1[2] + 0.10) else "\nRULE: T-LLM not better than R1",
          f"(P {t_[0]:.3f} >= 0.80? F1 {t_[2]:.3f} >= {r1[2] + 0.10:.3f}?)")
    _ = issue_of_pair


if __name__ == "__main__":
    {"build": build, "classify": classify, "score": score}[sys.argv[1]]()
