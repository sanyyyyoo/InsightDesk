"""
"One LLM does everything" baseline (rule: results/llm_batch_baseline_rule.md).

A: gpt-oss-120b (R1's judge model) gets ALL reviews of one product in one held-out half in a single
   prompt and returns groups; scored like R1 (fine-level human labels, final halves s0A, s1B, s1A).
   Stability: s0A run a second time (no cache) and compared.
B: the blind ChatGPT / Claude user-level sheets scored as batch systems against the approved
   user-level mapping (no calls).

  python experiments/dedup/llm_batch_baseline.py A
  python experiments/dedup/llm_batch_baseline.py B
"""

import json
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from ci_bootstrap import counts, prf  # noqa: E402
from spike_grouping import G, load  # noqa: E402

RES = os.path.join(HERE, "results")
CACHE = os.path.join(RES, "llm_batch_cache.jsonl")
B, SEED = 2000, 11

PROMPT = """Below are {n} app-store reviews of the customer-support app {product}.
Group together the reviews that report the SAME specific problem: the same feature AND the same concrete
symptom, so that one fix would solve all of them. Different wording does not matter. Being about the same
general area (e.g. both about login) is NOT enough. A review that names no concrete problem, or whose
problem appears only once, stays alone (do not list it).

Reviews:
{reviews}

Return JSON: {{"groups": [[id, id, ...], ...]}} listing only groups of 2 or more reviews (use the ids in brackets)."""


def llm():
    from e5_three_way import LLMJudge
    return LLMJudge(["x"], [0], "llm_batch", "founder_latest", "v1")      # only its key rotation is used


def group_once(j, product, refs, texts, tag, cache):
    key = json.dumps([tag, product, [int(r) for r in refs]])
    if key not in cache:
        reviews = "\n".join(f"[{int(r)}] " + " ".join(str(t).split()) for r, t in zip(refs, texts))
        prompt = PROMPT.format(n=len(refs), product=product, reviews=reviews)
        reply = j._call(prompt)
        cache[key] = {"groups": reply.get("groups", []), "prompt_chars": len(prompt)}
        with open(CACHE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, **cache[key]}) + "\n")
    lab = {int(r): f"{product}|s{int(r)}" for r in refs}
    valid = set(lab)
    for g, members in enumerate(cache[key]["groups"]):
        for m in members:
            try:
                m = int(m)
            except (TypeError, ValueError):
                continue
            if m in valid and lab[m].startswith(f"{product}|s"):          # first group wins
                lab[m] = f"{product}|g{g}"
    return lab


def pooled(parts):
    rng = np.random.default_rng(SEED)
    prep = []
    for issue, preds in parts:
        _, iss = np.unique(np.asarray(issue).astype(str), return_inverse=True)
        prep.append((iss, iss.max() + 1, {m: np.asarray(v).astype(str) for m, v in preds.items()}))
    names = list(parts[0][1])
    pt = {m: prf(*sum(np.array(counts(p[m], i, np.ones(n))) for i, n, p in prep)) for m in names}
    boot = {m: [] for m in names}
    for _ in range(B):
        tot = {m: np.zeros(3) for m in names}
        for i, n, p in prep:
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            for m in names:
                tot[m] += np.array(counts(p[m], i, w))
        for m in names:
            boot[m].append(prf(*tot[m]))
    lines = []
    for m in names:
        lo, hi = np.percentile(np.array(boot[m]), [2.5, 97.5], axis=0)
        lines.append(f"  {m:34s} P {pt[m][0]:.3f} [{lo[0]:.2f},{hi[0]:.2f}]  R {pt[m][1]:.3f} [{lo[1]:.2f},{hi[1]:.2f}]  "
                     f"F1 {pt[m][2]:.3f} [{lo[2]:.2f},{hi[2]:.2f}]")
    return lines


def part_a():
    cache = {}
    if os.path.exists(CACHE):
        for line in open(CACHE, encoding="utf-8"):
            r = json.loads(line)
            cache[r["key"]] = {"groups": r["groups"], "prompt_chars": r["prompt_chars"]}
    s = pd.read_csv(os.path.join(ROOT, "data", "external", "playstore_scored.csv")).set_index("complaint_ref")
    halves = {"s0A": load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
              "s1B": load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B"),
              "s1A": load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A")}
    j = llm()
    parts, chars, calls = [], 0, 0
    for name, r1 in halves.items():
        refs = list(r1.index)
        batch = {}
        for p in pd.unique(s.department.reindex(refs)):
            pr = [r for r in refs if s.department[r] == p]
            batch.update(group_once(j, p, pr, s.complaint_text.reindex(pr).tolist(), name, cache))
            chars += cache[json.dumps([name, p, [int(r) for r in pr]])]["prompt_chars"]
            calls += 1
        parts.append((s.issue_id.reindex(refs).astype(str).to_numpy(),
                      {"R1 (InsightDesk, online)": r1.reindex(refs).astype(str).to_numpy(),
                       "gpt-oss batch (one prompt per product)": np.array([batch[int(r)] for r in refs])}))
        print(f"{name}: done", flush=True)
    lines = ["\nA. PLAY STORE held-out halves pooled, fine-level human labels"] + pooled(parts)
    lines.append("  (R1 + re-joining RJ1 on the same halves: P 0.799 R 0.327 F1 0.464)")
    lines.append(f"  batch calls {calls}, prompt characters {chars} (~{chars // 4} tokens), "
                 f"~{chars / 4 / sum(len(p[0]) for p in parts):.0f} prompt tokens per review per run")
    # stability: s0A again, no cache (second run of the identical prompts)
    r1 = halves["s0A"]
    refs = list(r1.index)
    again = {}
    for p in pd.unique(s.department.reindex(refs)):
        pr = [r for r in refs if s.department[r] == p]
        again.update(group_once(j, p, pr, s.complaint_text.reindex(pr).tolist(), "s0A_rerun", cache))
    first = {}
    for p in pd.unique(s.department.reindex(refs)):
        pr = [r for r in refs if s.department[r] == p]
        first.update(group_once(j, p, pr, s.complaint_text.reindex(pr).tolist(), "s0A", cache))
    same = tot = 0
    for a in range(len(refs)):
        for b in range(a + 1, len(refs)):
            if s.department[refs[a]] != s.department[refs[b]]:
                continue
            tot += 1
            same += (first[refs[a]] == first[refs[b]]) == (again[refs[a]] == again[refs[b]])
    lines.append(f"  stability (s0A run twice, identical prompts): {same / tot:.1%} of review pairs grouped the same way")
    text = "\n".join(lines)
    print(text)
    open(os.path.join(RES, "llm_batch_baseline_A.txt"), "w", encoding="utf-8").write(text + "\n")


def part_b():
    u = pd.read_csv(os.path.join(ROOT, "data", "external", "playstore_user.csv")).set_index("complaint_ref")
    L = pd.read_csv(os.path.join(HERE, "labels", "playstore_final_labels.csv"))
    sheets = {}
    for k in ("claude", "gpt"):
        sh = pd.read_excel(os.path.join(HERE, "labelling", f"user_level_label_sheet_{k}.xlsx"), "Reviews")
        byrow = pd.Series(sh.sort_values("id").problem.astype(str).str.strip().values, index=L.row.values)
        p = u.row.map(byrow)
        lab = u.department + "|" + p
        nop = p.str.lower().eq("no_problem")
        lab[nop] = "single_" + lab.index.astype(str)[nop]
        sheets[k] = lab.astype(str)
    ids = np.array(sorted(set(u.issue_id)))
    issues = u.issue_id.to_numpy()
    lines = ["\nB. PLAY STORE user-level stream (364 reviews), approved user-level mapping as key"]
    for seed in (0, 1):
        rng = np.random.default_rng(seed)
        half = set(rng.choice(ids, size=len(ids) // 2, replace=False))
        a = u.index[np.isin(issues, list(half))]
        b = u.index[~np.isin(issues, list(half))]
        for h, test in (("B", b), ("A", a)):          # e5: half B tests the issues NOT drawn, half A the drawn ones
            if (seed, h) == (0, "B"):
                tag = "dev s0B"
            else:
                tag = f"s{seed}{h}"
            preds = {f"ChatGPT sheet (one LLM, batch)": sheets["gpt"].reindex(test).to_numpy(),
                     f"Claude sheet (one LLM, batch)": sheets["claude"].reindex(test).to_numpy()}
            f = os.path.join(RES, f"playstore_user_e5_assignments_llm_seeds{seed}_{G}_half{h}_founder_gated.csv")
            if os.path.exists(f):
                r1 = pd.read_csv(f).drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").case
                preds = {"R1 (InsightDesk, online)": r1.reindex(test).astype(str).to_numpy(), **preds}
            lines += [f"  -- {tag} ({len(test)} reviews)"] + pooled([(u.issue_id.reindex(test).astype(str).to_numpy(), preds)])
    text = "\n".join(lines)
    print(text)
    open(os.path.join(RES, "llm_batch_baseline_B.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    {"A": part_a, "B": part_b}[sys.argv[1]]()
