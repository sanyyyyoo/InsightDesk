"""Sensitivity checks (rule: results/sensitivity_rule.md). Report-only.

  python experiments/dedup/sensitivity.py
"""
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e5_three_way as e5  # noqa: E402
import spike_review as sr  # noqa: E402
import spike_sim as ss  # noqa: E402
from ci_bootstrap import counts, prf  # noqa: E402
from leak_breakdown import Judge  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from spike_grouping import G, load  # noqa: E402
from spike_grouping_v2 import setup  # noqa: E402

OUT = os.path.join(HERE, "results", "sensitivity_results.txt")
lines = ["SENSITIVITY CHECKS (rule: results/sensitivity_rule.md)"]


def say(s):
    lines.append(s)
    print(s, flush=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")


def part_a():
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    e5.MAX_CANDIDATES = 5
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    ids = np.array(sorted(set(issues)))
    halves = []
    for seed, half in ((0, "A"), (1, "B"), (1, "A")):
        rng = np.random.default_rng(seed)
        h = set(rng.choice(ids, size=len(ids) // 2, replace=False))
        a, b = np.where(np.isin(issues, list(h)))[0], np.where(~np.isin(issues, list(h)))[0]
        tune, test = (a, b) if half == "B" else (b, a)
        th, tl = e5.band_thresholds_wide(emb[tune], issues[tune], groups[tune])
        halves.append((test, th, tl))
    say("\nA2. Threshold grid around each half's calibrated thresholds (Play Store, 3 held-out halves pooled)")
    say("    calibrated (t_high, t_low) per half: " + ", ".join(f"({th:.3f}, {tl:.3f})" for _, th, tl in halves))
    for dl in (0.0, 0.04, 0.09, 0.14):
        for dh in (0.0, 0.03, 0.08, 0.13):
            tot, judged, n, miss = np.zeros(3), 0, 0, 0
            for test, th, tl in halves:
                judge = Judge(refs, issues, os.path.join(HERE, "results", "llm_judge_cache_playstore_founder_gated.jsonl"))
                labels, banded, _ = e5.by_group(lambda r: e5.three_way(emb, r, th - dh, tl + dl, judge, True), test, groups)
                lab = np.array([f"{groups[i]}|{l}" for i, l in zip(test, labels)])
                _, iss = np.unique(issues[test], return_inverse=True)
                tot += counts(lab, iss, np.ones(iss.max() + 1))
                judged += banded
                n += len(test)
                miss += judge.misses
            p, r, f = prf(*tot)[:3]
            say(f"  t_low +{dl:.2f}  t_high -{dh:.2f}   P {p:.3f}  R {r:.3f}  F1 {f:.3f} | judged {judged / n:.0%} | misses {miss}")


def ewma(alpha, L):
    def det(counts, first):
        n_units, n_w = counts.shape
        z = np.zeros(n_units)
        al = np.zeros_like(counts, dtype=bool)
        started = np.zeros(n_units, dtype=bool)
        for t in range(n_w):
            lam = sr.baseline(counts, first, t)
            live = first <= t
            z = np.where(live & ~started, lam, z)
            started |= live
            z = np.where(live, alpha * counts[:, t] + (1 - alpha) * z, 0.0)
            ucl = lam + L * np.sqrt(alpha / (2 - alpha) * lam)
            al[:, t] = live & (counts[:, t] >= 2) & (z > ucl)
        return al
    return det


def cusum_delta(h, delta):
    def det(counts, first):
        n_units, n_w = counts.shape
        S = np.zeros(n_units)
        al = np.zeros_like(counts, dtype=bool)
        for t in range(n_w):
            l0 = sr.baseline(counts, first, t)
            k = delta / np.log((l0 + delta) / l0)
            live = first <= t
            S = np.where(live, np.maximum(0.0, S + counts[:, t] - k), 0.0)
            fire = live & (S >= h)
            al[:, t] = fire
            S[fire] = 0.0
        return al
    return det


def part_bc():
    ps = setup("playstore")
    llm = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
    single = [load(f"playstore_e5_assignments_single_oracle_seeds0_{G}_halfA_merge", "single", 0, "A"),
              load(f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", "single", 1, "A"),
              load(f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", "single", 1, "B")]
    sets_ps = ss.methods_for(llm, single, *ps)
    sets_bug = []
    for data, sgl in (("firefox3", f"firefox3_e5_assignments_single_oracle_{G}_ext_playstore"),
                      ("thunderbird", f"thunderbird_e5_assignments_single_oracle_ceA_ceB_{G}_ext_playstore")):
        s = setup(data, "playstore")
        sets_bug += ss.methods_for([load(f"{data}_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", data)],
                                   [load(sgl, "single", "ext", data)], *s)
    for name, sets in (("Play Store", sets_ps), ("Firefox 3 + Thunderbird", sets_bug)):
        say(f"\nB. CUSUM grid, {name}: detection / false alerts per 100 windows (cases | alert groups)")
        for delta in (0.5, 1.0, 2.0):
            for h in (1.0, 1.5, 2.0, 3.0, 4.0):
                r = sr.run_sim(cusum_delta(h, delta), sets)
                c, gg = r["R1 cases"], r["R1 alert groups (v2)"]
                say(f"  delta {delta:.1f}  h {h:.1f}   cases {c[0]:.2f} / {c[1]:.2f}   groups {gg[0]:.2f} / {gg[1]:.2f}")
        say(f"\nC. EWMA baseline, {name}: detection / false alerts per 100 windows (cases | alert groups)")
        for alpha in (0.2, 0.3):
            for L in (2.0, 2.5, 3.0):
                r = sr.run_sim(ewma(alpha, L), sets)
                c, gg = r["R1 cases"], r["R1 alert groups (v2)"]
                say(f"  alpha {alpha:.1f}  L {L:.1f}   cases {c[0]:.2f} / {c[1]:.2f}   groups {gg[0]:.2f} / {gg[1]:.2f}")


def part_a3():
    from sentence_transformers import SentenceTransformer
    from normalize import boilerplate_suppress
    enc = SentenceTransformer(e5.EMBED_MODEL)
    e5.MAX_CANDIDATES = 5
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    ids = np.array(sorted(set(issues)))
    halves = []
    for seed, half in ((0, "A"), (1, "B"), (1, "A")):
        rng = np.random.default_rng(seed)
        h = set(rng.choice(ids, size=len(ids) // 2, replace=False))
        a, b = np.where(np.isin(issues, list(h)))[0], np.where(~np.isin(issues, list(h)))[0]
        tune, test = (a, b) if half == "B" else (b, a)
        th, tl = e5.band_thresholds_wide(emb[tune], issues[tune], groups[tune])
        halves.append((test, th, tl))
    say("\nA3. t_low sensitivity with LIVE judge calls (Play Store, 3 held-out halves pooled, calibrated t_high)")
    for dl in (0.0, 0.04, 0.09, 0.14):
        tot, judged, n = np.zeros(3), 0, 0
        for test, th, tl in halves:
            judge = e5.LLMJudge(texts, refs, "playstore", "founder", "gated")
            labels, banded, _ = e5.by_group(lambda r: e5.three_way(emb, r, th, tl + dl, judge, True), test, groups)
            lab = np.array([f"{groups[i]}|{l}" for i, l in zip(test, labels)])
            _, iss = np.unique(issues[test], return_inverse=True)
            tot += counts(lab, iss, np.ones(iss.max() + 1))
            judged += banded
            n += len(test)
        p, r, f = prf(*tot)[:3]
        say(f"  t_low +{dl:.2f}   P {p:.3f}  R {r:.3f}  F1 {f:.3f} | judged {judged / n:.0%}")


if __name__ == "__main__" and "--a3" in sys.argv:
    lines.extend(open(OUT, encoding="utf-8").read().splitlines()[1:])
    part_a3()
elif __name__ == "__main__":
    lines.extend(open(OUT, encoding="utf-8").read().splitlines()[1:])
    part_a()
