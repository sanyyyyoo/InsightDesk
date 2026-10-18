"""
Vague and area counters for spike detection (rule: results/vague_area_spike_rule.md). No LLM calls.

Streams: labelled real Play Store reviews of Zendesk and Freshdesk, with R1's real app decisions
(reports/replay/replay_assignments.csv). Outbreaks: S specific, V vague outage, A area outage.
Counters: C cases, C+V + product vague counter, C+V+A + area counters (gpt-oss or human areas).

  python experiments/dedup/vague_area_spike_sim.py
"""

import json
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from spike_sim import SEED, TRIALS, W, make_detector_v2  # noqa: E402

DET = make_detector_v2(2, 0.001)
REPLAY = "D:/PBL/InsightDesk-claude-review/reports/replay/replay_assignments.csv"
PRODUCTS = ("Zendesk", "Freshdesk")


def norm(x):
    return " ".join(str(x).lower().split())


def load():
    lab = pd.read_csv(os.path.join(HERE, "labels", "playstore_final_labels.csv"))
    cb = pd.read_csv(os.path.join(HERE, "labels", "playstore_codebook.csv")).set_index("problem_code")
    oss = pd.DataFrame([json.loads(line) for line in open(os.path.join(HERE, "results", "llm_labels_playstore.jsonl"),
                                                          encoding="utf-8")]).drop_duplicates("row", keep="last")
    lab["area_human"] = lab.problem_code.map(cb.area)
    lab["area_oss"] = lab.row.map(oss.set_index("row").code).map(cb.area)
    rep = pd.read_csv(REPLAY)
    rep = rep[~rep.is_synthetic.astype(bool)].drop_duplicates("complaint_text")
    rep["k"] = rep.complaint_text.map(norm)
    lab["k"] = lab.review_text.map(norm)
    d = lab.merge(rep[["k", "case_id", "route"]], on="k", how="inner")
    d = d[d["product"].isin(PRODUCTS)].reset_index(drop=True)
    d["vague"] = d.route.eq("vague")
    d["case"] = d.case_id.astype(str)
    return d


def counter_matrix(keys, win):
    codes, u = np.unique(keys, return_inverse=True)
    counts = np.zeros((len(codes), W))
    np.add.at(counts, (u, win), 1)
    first = np.full(len(codes), W)
    np.minimum.at(first, u, win)
    return codes, u, counts, first


def alerts_for(keys, win, is_out, valid=None):
    """Alerts of detector v2 on one counter family; hit windows / false alerts."""
    codes, u, counts, first = counter_matrix(keys, win)
    out = np.zeros((len(codes), W))
    np.add.at(out, (u[is_out], win[is_out]), 1)
    al = DET(counts, first)
    if valid is not None:                      # counters that exist (e.g. no area = no counter)
        al &= np.array([valid(c) for c in codes])[:, None]
    hit = al & (out > 0)
    false = al & (out == 0)
    return hit, int(false.sum())


def trial(d, kind, n, rng, area_col):
    """One simulated 30-day stream of one product with one outbreak. Returns per-config (hit, false)."""
    base = d.copy()
    base["win"] = rng.integers(0, W, len(base))
    b = int(rng.integers(60, 111))
    base["out"] = False
    if kind == "S":
        sizes = base.problem_code.value_counts()
        pool = [p for p, k in sizes.items() if k >= 5 and not p.endswith("_unspecified") and p != "not_a_problem"]
        p = pool[rng.integers(len(pool))]
        idx = np.where(base.problem_code.to_numpy() == p)[0]
        idx = idx[rng.permutation(len(idx))]
        nb = math.ceil(0.3 * len(idx))
        w = base.win.to_numpy().copy()
        w[idx[:nb]] = rng.integers(0, b, nb)
        w[idx[nb:]] = rng.integers(b, b + 2, len(idx) - nb)
        base["win"] = w
        base.loc[base.index[idx], "out"] = True
        stream = base
    else:
        if kind == "V":
            src = base[base.vague]
        else:
            areas = base[area_col].value_counts()
            areas = [a for a, k in areas.items() if k >= 5 and a not in ("Not a problem", "Other")]
            a = areas[rng.integers(len(areas))]
            src = base[base[area_col] == a]
        cp = src.iloc[rng.integers(0, len(src), n)].copy()
        cp["win"] = rng.integers(b, b + 2, n)
        cp["out"] = True
        new_case = ["inj_%d" % k for k in range(n)]
        cp["case"] = np.where(cp.vague, new_case, cp.case)         # vague copy = new singleton case
        stream = pd.concat([base, cp], ignore_index=True)
    w = stream.win.to_numpy()
    o = stream.out.to_numpy()
    win_ok = lambda h: bool(h[:, b:min(b + 3, W)].any())
    hc, fc = alerts_for(stream.case.to_numpy(), w, o)
    vk = np.where(stream.vague, "vague", "_specific")
    hv, fv = alerts_for(vk, w, o, valid=lambda c: c == "vague")
    ak = stream[area_col].fillna("_none").astype(str).to_numpy()
    ha, fa = alerts_for(ak, w, o, valid=lambda c: c not in ("_none", "Not a problem", "Other"))
    return {"C": (win_ok(hc), fc),
            "C+V": (win_ok(hc) or win_ok(hv), fc + fv),
            "C+V+A": (win_ok(hc) or win_ok(hv) or win_ok(ha), fc + fv + fa)}


def run(d, kind, n, area_col):
    rng = np.random.default_rng(SEED)
    per = TRIALS // len(PRODUCTS)
    tot = {k: [0, 0] for k in ("C", "C+V", "C+V+A")}
    for prod in PRODUCTS:
        dp = d[d["product"] == prod]
        for _ in range(per):
            r = trial(dp, kind, n, rng, area_col)
            for k, (h, f) in r.items():
                tot[k][0] += h
                tot[k][1] += f
    trials = per * len(PRODUCTS)
    return {k: (v[0] / trials, v[1] / trials / W * 100) for k, v in tot.items()}


def main():
    d = load()
    print(f"stream: {len(d)} labelled real reviews matched to the app replay | "
          + ", ".join(f"{p}: {int((d['product'] == p).sum())} ({int(d[d['product'] == p].vague.sum())} vague)"
                      for p in PRODUCTS))
    print(f"gpt-oss area missing for {int(d.area_oss.isna().sum())} reviews")
    res = {}
    for area_col, area_name in (("area_oss", "gpt-oss areas"), ("area_human", "human areas (upper bound)")):
        print(f"\n=== area counters from {area_name} ===")
        for kind, n in (("S", 0), ("V", 5), ("V", 10), ("V", 20), ("A", 10)):
            r = run(d, kind, n, area_col)
            res[(area_col, kind, n)] = r
            label = {"S": "S specific outbreak", "V": f"V vague outage n={n}", "A": f"A area outage n={n}"}[kind]
            print(f"  {label:24s} " + " | ".join(f"{k}: detected {v[0]:.2f}, false {v[1]:.2f}/100w" for k, v in r.items()))
    v = res[("area_oss", "V", 10)]
    s = res[("area_oss", "S", 0)]
    a = res[("area_oss", "A", 10)]
    ok_v = v["C+V"][0] >= 0.80 and s["C+V"][1] <= 1.25 * s["C"][1]
    ok_a = (a["C+V+A"][0] - a["C+V"][0]) >= 0.10 and s["C+V+A"][1] <= 1.25 * s["C+V"][1]
    print(f"\nRULE vague counter: {'ADOPT' if ok_v else 'not adopted'} (V n=10 detection {v['C+V'][0]:.2f} >= 0.80? "
          f"false {s['C+V'][1]:.2f} <= {1.25 * s['C'][1]:.2f}?)")
    print(f"RULE area counters (gpt-oss): {'ADOPT' if ok_a else 'not adopted'} (A gain {a['C+V+A'][0] - a['C+V'][0]:+.2f} >= 0.10? "
          f"false {s['C+V+A'][1]:.2f} <= {1.25 * s['C+V'][1]:.2f}?)")


if __name__ == "__main__":
    main()
