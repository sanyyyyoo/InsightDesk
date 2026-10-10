"""
Equivalence check: the app's R1 code (backend/services/dedup_r1.py) must build
exactly the same cases as the tested experiment pipeline.

Replays the frozen held-out runs (Play Store within-company halves s0A, s1A,
s1B and Firefox sample 3) complaint by complaint through dedup_r1 with an
in-memory vector store, answering every judge call from the experiments'
saved judge answers (no LLM calls, no network). Then compares the resulting
cases with the experiments' saved assignments, partition by partition.

Needs the experiments clone at D:/PBL/InsightDesk-dedup.

  python test_r1_equivalence.py
"""

import json
import os
import sys
import types

import numpy as np
import pandas as pd

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("OMP_NUM_THREADS", "4")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

EXP = "D:/PBL/InsightDesk-dedup"
# experiment scripts are importable, but `backend` must resolve to THIS app's code
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(EXP, "experiments", "dedup"))

from backend.services import dedup_r1  # noqa: E402

RES = os.path.join(EXP, "experiments", "dedup", "results")
G = "perproduct_wideband_exemplars_top5"


class MemoryStore:
    """In-memory stand-in for the Pinecone exemplar index."""

    def __init__(self):
        self.vecs = {}                       # id -> (vec, metadata)

    def query(self, vec, top_k, product=None):
        hits = [(md["case_id"], float(v @ vec), md) for v, md in self.vecs.values()
                if product is None or md.get("product") == product]
        hits.sort(key=lambda h: -h[1])
        return hits[:top_k]

    def exemplars(self, case_id):
        return [v for (v, md) in self.vecs.values() if md["case_id"] == case_id]

    def add(self, case_id, k, vec, metadata):
        md = {key: val for key, val in metadata.items() if val is not None}
        md["case_id"] = int(case_id)
        self.vecs[f"{case_id}:{k}"] = (np.asarray(vec, dtype=float), md)


def cached_judge(cache, misses):
    def judge(new_id, new_text, cands):
        key = json.dumps([int(new_id), [[int(c.founder_id)] for c in cands]])
        if key not in cache:
            misses.append(key)
            raise dedup_r1.JudgeError("no saved answer")
        a = cache[key]
        return (a != -1), (a if a > 0 else 0)
    return judge


def replay(rows, refs, emb, texts, depts, t_high, t_low, cache):
    store, misses = MemoryStore(), []
    judge = cached_judge(cache, misses)
    case_of, next_case = {}, 0
    for r in rows:
        d = dedup_r1.decide(int(refs[r]), emb[r], texts[r], product=depts[r], store=store, judge=judge,
                            t_high=t_high, t_low=t_low, top_k=5, require_top1=False)
        if d.case_id is not None:
            case_of[int(refs[r])] = d.case_id
            dedup_r1.add_member(d.target, emb[r], store=store)
        else:
            case_of[int(refs[r])] = next_case
            dedup_r1.start_case(next_case, emb[r], int(refs[r]), texts[r], product=depts[r],
                                vague=d.vague, store=store)
            next_case += 1
    return case_of, misses


def same_partition(app, exp):
    """Complaints whose case membership differs (partition comparison, ids ignored)."""
    a2e, e2a, bad = {}, {}, []
    for ref, ca in app.items():
        ce = exp[ref]
        if a2e.setdefault(ca, ce) != ce or e2a.setdefault(ce, ca) != ca:
            bad.append(ref)
    return bad


def load_exp(f, judge, seed, half):
    a = pd.read_csv(os.path.join(RES, f + ".csv"))
    a = a[(a.judge == judge) & (a.split_seed.astype(str) == str(seed)) & (a.held_out_half == half)]
    return a.drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").case.to_dict()


def load_cache(name):
    cache = {}
    for line in open(os.path.join(RES, f"llm_judge_cache_{name}.jsonl"), encoding="utf-8"):
        r = json.loads(line)
        cache[r["key"]] = r["answer"]
    return cache


def prepare(data, calibrate_on=None):
    from sentence_transformers import SentenceTransformer

    from e5_three_way import EMBED_MODEL, EXT_REF_OFFSET
    from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress
    from replay_lab import load_ground_truth
    enc = SentenceTransformer(EMBED_MODEL)
    cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
    if calibrate_on:
        cal = load_ground_truth(path=os.path.join(EXP, DATA_PATHS[calibrate_on]))
        tgt = load_ground_truth(path=os.path.join(EXP, DATA_PATHS[data]))
        tgt["complaint_ref"] = tgt["complaint_ref"] + EXT_REF_OFFSET
        raw = pd.concat([cal[cols].assign(_cal=True), tgt[cols].assign(_cal=False)], ignore_index=True)
    else:
        raw = load_ground_truth(path=os.path.join(EXP, DATA_PATHS[data]))
    df = apply_text_mode(raw, "boilerplate", enc)
    texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    return df, texts, emb


def main():
    cwd = os.getcwd()
    os.chdir(EXP)                                    # experiment data paths are relative to the clone
    from e5_three_way import band_thresholds_wide
    results = []
    try:
        df, texts, emb = prepare("playstore")
        refs, issues = df.complaint_ref.to_numpy(), np.array(df.issue_id.astype(str).tolist())
        depts = df.department.astype(str).to_numpy()
        issue_ids = np.array(sorted(set(issues)))
        cache = load_cache("playstore_founder_gated")
        for seed, h, f in [(0, "A", f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated"),
                           (1, "A", f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated"),
                           (1, "B", f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated")]:
            rng = np.random.default_rng(seed)
            half = set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))
            a = np.where(np.isin(issues, list(half)))[0]
            b = np.where(~np.isin(issues, list(half)))[0]
            tune, test = (a, b) if h == "B" else (b, a)
            t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], depts[tune])
            app, misses = replay(test, refs, emb, texts, depts, t_high, t_low, cache)
            bad = same_partition(app, load_exp(f, "llm", seed, h))
            results.append((f"Play Store s{seed}{h}", len(test), len(bad), len(misses)))

        df, texts, emb = prepare("firefox3", calibrate_on="playstore")
        refs, issues = df.complaint_ref.to_numpy(), np.array(df.issue_id.astype(str).tolist())
        depts = df.department.astype(str).to_numpy()
        is_cal = df["_cal"].to_numpy(dtype=bool)
        t_high, t_low = band_thresholds_wide(emb[is_cal], issues[is_cal], depts[is_cal])
        test = np.where(~is_cal)[0]
        app, misses = replay(test, refs, emb, texts, depts, t_high, t_low, load_cache("firefox3_ext_playstore_founder_gated"))
        bad = same_partition(app, load_exp(f"firefox3_e5_assignments_llm_{G}_founder_gated_ext_playstore",
                                           "llm", "ext", "firefox3"))
        results.append(("Firefox 3", len(test), len(bad), len(misses)))
    finally:
        os.chdir(cwd)
    ok = True
    for name, n, bad, miss in results:
        good = bad == 0 and miss == 0
        ok &= good
        print(f"{'ok  ' if good else 'FAIL'} {name}: {n} complaints, {bad} assigned differently, "
              f"{miss} judge calls without a saved answer")
    print("ALL PASSED" if ok else "SOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
