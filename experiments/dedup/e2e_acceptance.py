"""
End-to-end acceptance test (rule: results/e2e_acceptance_rule.md, with its 2026-10-14 amendment).

For real user-level problems that burst within 12 hours, does InsightDesk (R1 as deployed + spike
detector v2 on cases, alert groups and the unassigned counter + escalation policy) show a case with a
realistic count, alert in time and make the case eligible for escalation - with few false alarms?
Streams: labelled Play Store reviews of Zendesk and Freshdesk; every review appears once; incident
problems burst at non-overlapping times (no copies, see the amendment).

  python experiments/dedup/e2e_acceptance.py --judge oracle    # code check, no API calls
  python experiments/dedup/e2e_acceptance.py                    # the real run (R1, gated LLM judge)
"""

import argparse
import math
import os
import sys

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
import e5_three_way as e5  # noqa: E402
from e5_three_way import LLMJudge, OracleJudge, three_way  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402
from spike_grouping_v2 import alert_groups  # noqa: E402
from spike_sim import make_detector_v2  # noqa: E402

W = 120                      # six-hour windows = 30 days
T_HIGH, T_LOW = 0.8306, 0.26  # as deployed in the app
CASE_DET, GROUP_DET, UNASSIGNED_DET = make_detector_v2(2, 0.001), make_detector_v2(3, 0.001), make_detector_v2(2, 0.001)
PRODUCTS = ("Zendesk", "Freshdesk")
OUT = os.path.join(HERE, "results")


def wilson(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def build_stream(rows, issues, rng, incidents=True):
    """Window per row; returns (window array, [(problem, b)])."""
    win = rng.integers(0, W, len(rows))
    plan = []
    if incidents:
        sizes = pd.Series(issues[rows]).value_counts()
        problems = [p for p, n in sizes.items() if n >= 5]
        rng.shuffle(problems)
        slots = list(range(20, 113, 6))              # b at least 6 windows apart
        rng.shuffle(slots)
        for p, b in zip(problems, slots):
            idx = np.where(issues[rows] == p)[0]
            idx = idx[rng.permutation(len(idx))]
            nb = math.ceil(0.3 * len(idx))
            win[idx[:nb]] = rng.integers(0, b, nb)
            win[idx[nb:]] = rng.integers(b, b + 2, len(idx) - nb)
            plan.append((p, int(b)))
    return win, plan


def unit_alerts(keys, win, det):
    codes, u = np.unique(np.asarray(keys).astype(str), return_inverse=True)
    counts = np.zeros((len(codes), W))
    np.add.at(counts, (u, win), 1)
    first = np.full(len(codes), W)
    np.minimum.at(first, u, win)
    return codes, u, det(counts, first)


def evaluate(rows, win, plan, case, vague_rows, issues, emb, refs, product):
    """Per-incident measures for one stream."""
    case = np.asarray(case).astype(str)
    c_codes, c_u, c_al = unit_alerts(case, win, CASE_DET)
    a = pd.Series(case, index=refs[rows])
    pos = {r: k for k, r in enumerate(refs)}
    grp = alert_groups(a, pos, emb, np.array([product] * len(refs)), 99).to_numpy().astype(str)
    multi = pd.Series(case).groupby(grp).nunique()
    g_codes, g_u, g_al = unit_alerts(grp, win, GROUP_DET)
    g_al &= np.array([multi.get(g, 1) >= 2 for g in g_codes])[:, None]     # groups joining >= 2 cases
    is_vague = np.array([r in vague_rows for r in rows])
    v_codes, v_u, v_al = unit_alerts(np.where(is_vague, "unassigned", "_specific"), win, UNASSIGNED_DET)
    v_al &= (v_codes == "unassigned")[:, None]
    case_vague = pd.Series(is_vague).groupby(case).first()                # a case started by a vague complaint
    out = []
    for p, b in plan:
        inc = issues[rows] == p
        sl = slice(b, min(b + 2, W))
        hit = lambda u, al: bool(al[np.unique(u[inc & (win >= b) & (win <= b + 1)])][:, sl].any()) if (inc & (win >= b) & (win <= b + 1)).any() else False
        alerted = hit(c_u, c_al) or hit(g_u, g_al) or hit(v_u, v_al)
        # escalation-eligible by end of window b+1: a non-vague case with incident complaints and >= 3 reports
        # so far, or spiking (case or its alert group) in b..b+1
        eligible = False
        for cc in np.unique(case[inc]):
            if case_vague.get(cc, False):
                continue
            members = case == cc
            n_by = int((members & (win <= b + 1)).sum())
            ci = np.where(c_codes == cc)[0][0]
            gi = np.where(g_codes == grp[members][0])[0][0]
            if n_by >= 3 or c_al[ci, sl].any() or g_al[gi, sl].any():
                eligible = True
                break
        sizes = pd.Series(case[inc]).value_counts()
        gsz = pd.Series(grp[inc]).value_counts()
        out.append({"product": product, "problem": p, "b": b, "reviews": int(inc.sum()),
                    "cases": int(len(sizes)), "largest_case_share": float(sizes.iloc[0] / inc.sum()),
                    "largest_group_share": float(gsz.iloc[0] / inc.sum()),
                    "alerted_12h": alerted, "escalation_eligible_12h": eligible,
                    "vague_share": float(is_vague[inc].mean())})
    return out


def false_alarms(rows, win, case, vague_rows, emb, refs, product):
    case = np.asarray(case).astype(str)
    a = pd.Series(case, index=refs[rows])
    pos = {r: k for k, r in enumerate(refs)}
    grp = alert_groups(a, pos, emb, np.array([product] * len(refs)), 99).to_numpy().astype(str)
    multi = pd.Series(case).groupby(grp).nunique()
    _, _, c_al = unit_alerts(case, win, CASE_DET)
    g_codes, _, g_al = unit_alerts(grp, win, GROUP_DET)
    g_al &= np.array([multi.get(g, 1) >= 2 for g in g_codes])[:, None]
    is_vague = np.array([r in vague_rows for r in rows])
    v_codes, _, v_al = unit_alerts(np.where(is_vague, "unassigned", "_specific"), win, UNASSIGNED_DET)
    v_al &= (v_codes == "unassigned")[:, None]
    n = int(c_al.sum() + g_al.sum() + v_al.sum())
    return n, n / (W / 28)                         # alerts, alerts per week (28 windows = 7 days)


def run_dedup(order, emb, judge):
    labels, _, _ = three_way(emb, order, T_HIGH, T_LOW, judge, exemplars=True)
    return labels


JUDGE_NAME = {"playstore_user": "playstore", "firefox3": "firefox3_ext_playstore"}
PAIR_NAME = {"playstore_user": "playstore", "firefox3": "firefox3"}


def rejoin_stream(rows, case, vague_rows, emb, texts, refs, prods, data):
    """One RJ1 pass over the stream's final cases (positions, so injected copies stay separate).
    Applied once to the whole stream: optimistic on timing vs a periodic pass in deployment."""
    import rejoin as rj
    pos = np.arange(len(rows))
    r = dict(emb=emb[rows], groups=prods[rows], test=pos, labels=np.asarray(case), issues=np.zeros(len(rows), int),
             vague={k for k in pos if rows[k] in vague_rows}, t_low=T_LOW)
    pj = rj.PairJudge([texts[i] for i in rows], refs[rows], PAIR_NAME[data])
    new, merges, _ = rj.run_variant(r, pj, 1)
    print(f"  re-joining: {len(merges)} merges", flush=True)
    return new


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--judge", default="llm", choices=["llm", "oracle"])
    ap.add_argument("--data", default="playstore_user", choices=["playstore_user", "firefox3"])
    ap.add_argument("--rejoin", action="store_true", help="add one RJ1 re-joining pass (rejoin_rule.md) to the stream's cases")
    args = ap.parse_args()
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    e5.MAX_CANDIDATES = 5
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS[args.data]), "boilerplate", enc)
    texts = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    refs = df["complaint_ref"].to_numpy()
    prods = df["department"].astype(str).to_numpy()
    llm = LLMJudge(texts, refs, JUDGE_NAME[args.data], "founder", "gated") if args.judge == "llm" else None
    rows_all, alarms = [], []
    for product in (PRODUCTS if args.data == "playstore_user" else ("Firefox",)):
        base = np.where(prods == product)[0]
        for seed in (7, 8, 99):
            rng = np.random.default_rng(seed)
            win, plan = build_stream(base, issues, rng, incidents=seed != 99)
            order_key = win * 1000 + rng.permutation(len(base))       # arrival order: window, then random
            perm = np.argsort(order_key)
            rows, win = base[perm], win[perm]
            judge = llm if llm is not None else OracleJudge(issues)
            if llm is not None:
                llm.vague = set()
            case = run_dedup(rows, emb, judge)
            vague_rows = set(getattr(judge, "vague", set()))
            if args.rejoin:
                case = rejoin_stream(rows, case, vague_rows, emb, texts, refs, prods, args.data)
            if seed == 99:
                n, per_week = false_alarms(rows, win, case, vague_rows, emb, refs, product)
                alarms.append({"product": product, "alerts": n, "per_week": per_week})
                print(f"{product} null stream: {n} alerts in 30 days ({per_week:.2f} per week)", flush=True)
            else:
                res = evaluate(rows, win, plan, case, vague_rows, issues, emb, refs, product)
                for r in res:
                    r["seed"] = seed
                rows_all += res
                print(f"{product} seed {seed}: {len(res)} incidents", flush=True)
    d = pd.DataFrame(rows_all)
    tag = ("" if args.data == "playstore_user" else "_" + args.data) + ("" if args.judge == "llm" else "_oracle_check") + ("_rejoin" if args.rejoin else "")
    d.to_csv(os.path.join(OUT, f"e2e_acceptance_incidents{tag}.csv"), index=False)
    n = len(d)
    lines = [f"END-TO-END ACCEPTANCE ({('R1 + RJ1 re-joining' if args.rejoin else 'R1 as deployed') if args.judge == 'llm' else 'ORACLE JUDGE - code check only'}), "
             f"{n} incidents, {args.data} " + str(d['product'].value_counts().to_dict())]
    for col, bar, name in (("alerted_12h", 0.80, "alerted within 12 h"), ("escalation_eligible_12h", 0.70, "escalation-eligible within 12 h")):
        k = int(d[col].sum())
        lo, hi = wilson(k, n)
        lines.append(f"  {name:34s} {k}/{n} = {k / n:.0%} [{lo:.0%},{hi:.0%}]  bar {bar:.0%} -> {'PASS' if k / n >= bar else 'FAIL'}")
    mc, mg = d.largest_case_share.median(), d.largest_group_share.median()
    lines.append(f"  median count captured: largest case {mc:.0%}, alert group {mg:.0%}  (bar case >= 50% or group >= 70%) -> "
                 f"{'PASS' if mc >= 0.5 or mg >= 0.7 else 'FAIL'}")
    lines.append(f"  median cases per incident {d.cases.median():.0f}; incidents' complaints marked unassigned: {d.vague_share.mean():.0%}")
    fa = pd.DataFrame(alarms)
    worst = fa.per_week.max() if len(fa) else float("nan")
    lines.append("  false alarms (null streams): " + ", ".join(f"{r.product} {r.per_week:.2f}/week" for r in fa.itertuples())
                 + f"  (bar <= 1 per product per week) -> {'PASS' if worst <= 1 else 'FAIL'}")
    lines.append("  RCA right-symptom: second step (rca sheet), not in this run")
    text = "\n".join(lines)
    print(text)
    open(os.path.join(OUT, f"e2e_acceptance_results{tag}.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
