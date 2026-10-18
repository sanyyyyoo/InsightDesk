"""
Spike-detection simulation (rule: results/spike_sim_rule.md). No LLM calls.

Counts complaints per unit (case, alert group, or true problem) in 6-hour
windows of a simulated 30-day stream with an injected outbreak, and runs the
app's z-score detector on each counting method.

  python experiments/dedup/spike_sim.py            # Play Store + Firefox sample 1
  python experiments/dedup/spike_sim.py --firefox2 # Firefox sample 2
"""

import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from spike_grouping import G, load  # noqa: E402
from spike_grouping_v2 import alert_groups, setup  # noqa: E402

W, TRIALS, SEED, Q = 120, 300, 5, 99
DETECTOR = None   # set in main


def detector_app(counts, first=None):
    """The app as it really runs: complaint_windows rows exist only for windows
    with >= 1 complaint, so history skips empty windows. detect_spike needs
    >= 7 rows, then compute_z_score needs >= 7 PRIOR rows; std = 0 -> no spike."""
    alerts = np.zeros_like(counts, dtype=bool)
    for u in np.where((counts > 0).sum(axis=1) >= 8)[0]:
        ts = np.where(counts[u] > 0)[0]
        vals = counts[u, ts]
        for k in range(7, len(ts)):
            h = vals[:k]
            sd = h.std()
            if sd > 0 and (vals[k] - h.mean()) / sd > 2:
                alerts[u, ts[k]] = True
    return alerts


def make_detector_v2(m, p, L=28, a=0.5, b=7):
    """Detector v2 (results/spike_detector_v2_rule.md): zero-filled windows, smoothed
    7-day baseline, alert when count >= m and the Poisson tail probability < p."""
    from scipy.stats import poisson

    def det(counts, first):
        n_units, n_w = counts.shape
        cs = np.concatenate([np.zeros((n_units, 1)), np.cumsum(counts, axis=1)], axis=1)
        alerts = np.zeros_like(counts, dtype=bool)
        for t in range(n_w):
            lo = np.maximum(first, t - L)
            n = np.maximum(t - lo, 0)
            s_ = cs[np.arange(n_units), t] - cs[np.arange(n_units), np.minimum(lo, t)]
            lam = (s_ + a) / (n + b)
            c = counts[:, t]
            cand = (c >= m) & (first <= t)
            if cand.any():
                alerts[cand, t] = poisson.sf(c[cand] - 1, lam[cand]) < p
        return alerts
    return det


def detector(counts, first):
    """App detector on a units x windows count matrix -> boolean alerts (z > 2)."""
    n_units, n_w = counts.shape
    cs = np.cumsum(counts, axis=1)
    cs2 = np.cumsum(counts ** 2, axis=1)
    alerts = np.zeros_like(counts, dtype=bool)
    for t in range(1, n_w):
        n = t - first                                   # history windows: first .. t-1
        ok = n >= 7
        if not ok.any():
            continue
        before = np.where(first > 0, cs[np.arange(n_units), np.maximum(first - 1, 0)], 0)
        before2 = np.where(first > 0, cs2[np.arange(n_units), np.maximum(first - 1, 0)], 0)
        s = cs[:, t - 1] - before
        s2 = cs2[:, t - 1] - before2
        nn = np.maximum(n, 1)
        mean = s / nn
        var = np.maximum(s2 / nn - mean ** 2, 0)
        std = np.sqrt(var)
        z = np.where((std > 0) & ok, (counts[:, t] - mean) / np.where(std > 0, std, 1), 0)
        alerts[:, t] = z > 2
    return alerts


def simulate(name, sets, rng, trials=TRIALS):
    """sets: list of (issues, methods), each an independent stream; trials split evenly."""
    tot = {}
    for issues, methods in sets:
        r = one_stream(issues, methods, rng, trials // len(sets))
        for m, v in r.items():
            t = tot.setdefault(m, {"det": 0, "delay": [], "false": 0, "n": 0})
            t["det"] += v["det"]; t["delay"] += v["delay"]; t["false"] += v["false"]; t["n"] += trials // len(sets)
    print(f"\n{name}  ({trials} trials over {len(sets)} stream(s))")
    for m, r in tot.items():
        d = np.mean(r["delay"]) if r["delay"] else float("nan")
        print(f"  {m:22s} detected={r['det'] / r['n']:.2f}  mean delay={d:.2f} windows  "
              f"false alerts/100 windows={r['false'] / r['n'] / W * 100:.2f}")
    return tot


def one_stream(issues, methods, rng, trials):
    """issues: array of true problem per complaint; methods: {name: array of unit per complaint}."""
    sizes = pd.Series(issues).value_counts()
    pool = [p for p, n in sizes.items() if n >= 5 and not str(p).startswith("lone")]
    res = {m: {"det": 0, "delay": [], "false": 0} for m in methods}
    for _ in range(trials):
        p = pool[rng.integers(len(pool))]
        b = int(rng.integers(60, 111))
        win = rng.integers(0, W, size=len(issues))
        idx = np.where(issues == p)[0]
        idx = idx[rng.permutation(len(idx))]
        nb = math.ceil(0.3 * len(idx))
        win[idx[:nb]] = rng.integers(0, b, size=nb)
        win[idx[nb:]] = rng.integers(b, b + 2, size=len(idx) - nb)
        is_p = issues == p
        for m, unit in methods.items():
            codes, u = np.unique(unit, return_inverse=True)
            counts = np.zeros((len(codes), W), dtype=float)
            np.add.at(counts, (u, win), 1)
            pc = np.zeros((len(codes), W), dtype=float)
            np.add.at(pc, (u[is_p], win[is_p]), 1)
            first = np.full(len(codes), W)
            np.minimum.at(first, u, win)
            al = DETECTOR(counts, first)
            hit = [t for t in range(b, min(b + 3, W)) if (al[:, t] & (pc[:, t] > 0)).any()]
            if hit:
                res[m]["det"] += 1
                res[m]["delay"].append(hit[0] - b)
            res[m]["false"] += int((al & (pc == 0)).sum())
    return res


def methods_for(parts_llm, parts_single, df, pos, emb, dept):
    """One independent stream per partition."""
    sets = []
    for a, s in zip(parts_llm, parts_single):
        refs = a.index
        issues = df.issue_id.reindex(refs).astype(str).to_numpy()
        sets.append((issues, {"R1 cases": a.astype(str).to_numpy(),
                              "R1 alert groups (v2)": alert_groups(a, pos, emb, dept, Q).astype(str).to_numpy(),
                              "true problems": issues,
                              "cosine-only cases": s.reindex(refs).astype(str).to_numpy()}))
    return sets


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--firefox2", action="store_true")
    ap.add_argument("--detector", default="app",
                    help="app = as deployed; zerofill = empty windows count as 0; v2:M:P = detector v2; select = v2 grid")
    args = ap.parse_args()
    global DETECTOR
    if args.detector == "select":
        return select_v2()
    if args.detector.startswith("v2:"):
        _, m, p = args.detector.split(":")
        DETECTOR = make_detector_v2(int(m), float(p))
    else:
        DETECTOR = detector_app if args.detector == "app" else detector
    print("detector:", args.detector)
    rng = np.random.default_rng(SEED)
    if args.firefox2:
        ff2 = setup("firefox2", "playstore")
        f = f"firefox2_e5_assignments_{{}}_{G}_ext_playstore"
        simulate("Firefox sample 2", methods_for(
            [load(f.format("llm") .replace(f"_{G}_", f"_{G}_founder_gated_"), "llm", "ext", "firefox2")],
            [load(f.format("single_oracle"), "single", "ext", "firefox2")], *ff2), rng)
        return
    ps = setup("playstore")
    llm = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
    single = [load(f"playstore_e5_assignments_single_oracle_seeds0_{G}_halfA_merge", "single", 0, "A"),
              load(f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", "single", 1, "A"),
              load(f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", "single", 1, "B")]
    simulate("Play Store within-company (3 halves, separate streams)", methods_for(llm, single, *ps), rng)
    ff = setup("firefox", "playstore")
    simulate("Firefox sample 1", methods_for(
        [load(f"firefox_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox")],
        [load(f"firefox_e5_assignments_single_oracle_{G}_ext_playstore", "single", "ext", "firefox")], *ff), rng)


def select_v2():
    """Grid on seen data, R1 cases only (rule: spike_detector_v2_rule.md)."""
    global DETECTOR
    ps = setup("playstore")
    llm = [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA_founder_gated", "llm", 0, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "A"),
           load(f"playstore_e5_assignments_llm_seeds1_{G}_founder_gated", "llm", 1, "B")]
    ff = setup("firefox", "playstore")
    ffa = [load(f"firefox_e5_assignments_llm_{G}_founder_gated_ext_playstore", "llm", "ext", "firefox")]

    def cases_only(parts, df):
        return [(df.issue_id.reindex(a.index).astype(str).to_numpy(), {"R1 cases": a.astype(str).to_numpy()})
                for a in parts]
    sets = {"Play Store": cases_only(llm, ps[0]), "Firefox 1": cases_only(ffa, ff[0])}
    rows = []
    for m in (2, 3, 4):
        for p in (0.01, 0.001):
            DETECTOR = make_detector_v2(m, p)
            r = {k: simulate(f"m={m} p={p}  {k}", v, np.random.default_rng(SEED))["R1 cases"] for k, v in sets.items()}
            det = {k: v["det"] / v["n"] for k, v in r.items()}
            fa = {k: v["false"] / v["n"] / W * 100 for k, v in r.items()}
            rows.append((m, p, np.mean(list(det.values())), max(fa.values())))
    ok = [r for r in rows if r[3] <= 2]
    print(chr(10) + "m p mean_detection max_false_per_100")
    for r in rows:
        print(f"{r[0]} {r[1]:<6} {r[2]:.3f} {r[3]:.2f}" + ("" if r in ok else "  (too many false alerts)"))
    if ok:
        best = max(ok, key=lambda r: (round(r[2], 4), r[0], -r[1]))
        print(f"{chr(10)}selected: m={best[0]} p={best[1]}")
    else:
        print(chr(10) + "no setting keeps false alerts <= 2 per 100 windows: v2 rejected at selection")


if __name__ == "__main__":
    main()
