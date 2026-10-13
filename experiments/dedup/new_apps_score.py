"""
Score R1 and the A/B variants on the new help-desk apps against the two LLM answer keys
(rule: results/new_apps_rule.md). No LLM calls.

Keys: data/external/new_apps/sheetX_*.xlsx and sheetY_*.xlsx (blind sheets; id = row of
new_apps_test588.csv). Same app + same code = duplicate; "vague", "<app>_VAGUE" and "other"
are not grouped (each its own singleton). Agreed key = pairs both keys call duplicates
(transitively closed); pairs only one key calls duplicates are left out of that score.

  python experiments/dedup/new_apps_score.py
"""

import glob
import os
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import adjusted_rand_score, cohen_kappa_score

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
from ci_bootstrap import counts, prf  # noqa: E402

NA = os.path.join(ROOT, "data", "external", "new_apps")
RES = os.path.join(HERE, "results")
APP = "D:/PBL/InsightDesk-claude-review/reports"
B, SEED = 2000, 11
TAG = "perproduct_wideband_exemplars_top5"


def key(path):
    d = pd.read_excel(path, "Reviews").set_index("id").sort_index()
    c = d.problem_code.astype(str).str.strip()
    ungrouped = c.str.lower().isin(["vague", "other", "nan", ""]) | c.str.upper().str.endswith("_VAGUE")
    lab = d.app + "|" + c
    lab[ungrouped] = "single_" + d.index[ungrouped].astype(str)
    return lab, ungrouped


def pairs_same(lab, apps):
    """Upper-triangle same-label vector over within-app pairs."""
    out = []
    for a in apps.unique():
        idx = np.where(apps.to_numpy() == a)[0]
        v = lab.to_numpy()[idx]
        iu = np.triu_indices(len(idx), 1)
        out.append(v[iu[0]] == v[iu[1]])
    return np.concatenate(out)


def agreed(kx, ky):
    """Connected components of pairs that BOTH keys group."""
    parent = list(range(len(kx)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    x, y = kx.to_numpy(), ky.to_numpy()
    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            if x[i] == x[j] and y[i] == y[j] and not x[i].startswith("single_"):
                parent[find(i)] = find(j)
    return pd.Series([f"agree_{find(i)}" for i in range(len(x))], index=kx.index)


def prep(case, issue, n_iss):
    """Contingency cells for fast weighted pair counts (same result as ci_bootstrap.counts)."""
    _, cidx = np.unique(case, return_inverse=True)
    cells, n_cell = np.unique(np.stack([cidx, issue]), axis=1, return_counts=True)
    return cells[0], cells[1], n_cell.astype(float), np.bincount(issue, minlength=n_iss).astype(float)


def fast_counts(pc, w):
    """Corrected cluster-bootstrap counting (same rule as ci_bootstrap.counts), on pre-built cells."""
    cc, ci, n_cell, n_iss = pc
    c2 = lambda x: x * (x - 1) / 2.0
    wi = w[ci]
    tp = float((wi * c2(n_cell)).sum())
    N = n_cell * wi
    cross = (np.bincount(cc, weights=N) ** 2 - np.bincount(cc, weights=N ** 2)) / 2.0
    true = float((w * c2(n_iss)).sum())
    return np.array([tp, tp + float(cross.sum()), true])


def score(name, preds, label, apps, rng_seed=SEED):
    """preds: {method: Series id->case}; pooled over apps, cluster bootstrap over key groups per app."""
    rng = np.random.default_rng(rng_seed)
    parts = []
    for a in apps.unique():
        ids = apps.index[apps == a]
        codes, issue = np.unique(label.reindex(ids).astype(str).to_numpy(), return_inverse=True)
        cases = {m: prep(p.reindex(ids).astype(str).to_numpy(), issue, len(codes)) for m, p in preds.items()}
        parts.append((a, issue, len(codes), cases))
    lines = [f"\n{name}"]
    true = sum(fast_counts(c[next(iter(c))], np.ones(n))[2] for _, i, n, c in parts)
    lines.append(f"  ({int(true)} duplicate pairs in the key, {sum(len(i) for _, i, _, _ in parts)} reviews)")
    point, boot = {}, {m: [] for m in preds}
    for m in preds:
        tot = np.zeros(3)
        for _, issue, n, cases in parts:
            tot += fast_counts(cases[m], np.ones(n))
        point[m] = prf(*tot)
    for _ in range(B):
        tot = {m: np.zeros(3) for m in preds}
        for _, issue, n, cases in parts:
            w = np.bincount(rng.integers(0, n, n), minlength=n).astype(float)
            for m in preds:
                tot[m] += fast_counts(cases[m], w)
        for m in preds:
            boot[m].append(prf(*tot[m]))
    arr = {m: np.array(v) for m, v in boot.items()}
    lines.append(f"  {'method':34s} {'precision':>20s} {'recall':>20s} {'F1':>20s} {'B3 P':>6s} {'B3 F1':>6s}")
    for m in preds:
        lo, hi = np.percentile(arr[m], [2.5, 97.5], axis=0)
        cells = [f"{point[m][j]:.3f} [{lo[j]:.2f},{hi[j]:.2f}]" for j in range(3)]
        bp, bf = bcubed(preds[m], label, apps)
        lines.append(f"  {m:34s} {cells[0]:>20s} {cells[1]:>20s} {cells[2]:>20s} {bp:6.3f} {bf:6.3f}")
    ref = next(iter(preds))
    for m in preds:
        if m == ref:
            continue
        d = arr[m] - arr[ref]
        lo, hi = np.percentile(d, [2.5, 97.5], axis=0)
        lines.append(f"  {m} minus {ref}: P {point[m][0] - point[ref][0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}], "
                     f"F1 {point[m][2] - point[ref][2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
    return lines


def bcubed(pred, label, apps):
    p_sum = r_sum = 0.0
    n = 0
    for a in apps.unique():
        ids = apps.index[apps == a]
        c = pred.reindex(ids).astype(str).to_numpy()
        t = label.reindex(ids).astype(str).to_numpy()
        for i in range(len(ids)):
            sc, st = c == c[i], t == t[i]
            p_sum += (sc & st).sum() / sc.sum()
            r_sum += (sc & st).sum() / st.sum()
            n += 1
    p, r = p_sum / n, r_sum / n
    return p, 2 * p * r / (p + r)


def harness(data, judge, file_tag, ids_of_ref):
    f = os.path.join(RES, f"{data}_e5_assignments_{file_tag}.csv")
    if not os.path.exists(f):
        return None
    a = pd.read_csv(f)
    a = a[a.judge == judge].drop_duplicates("complaint_ref", keep="last")
    s = pd.Series(a.case.to_numpy(), index=a.complaint_ref.map(ids_of_ref)).dropna()
    s.index = s.index.astype(int)
    return s


def app_replay(folder, test_rows):
    """replay_assignments.csv row -> sheet id (row order of the replay input file)."""
    a = pd.read_csv(os.path.join(APP, folder, "replay_assignments.csv"))
    a = a.sort_values("row")
    return pd.Series((a["product"].astype(str) + "|" + a.case_id.astype(str)).to_numpy(),
                     index=test_rows[a.row.to_numpy()])


def main():
    t = pd.read_csv(os.path.join(NA, "new_apps_test588.csv"))
    apps = t["product"].copy()
    apps.index = t.index
    sx, sy = sorted(glob.glob(os.path.join(NA, "sheetX_*.xlsx")))[0], sorted(glob.glob(os.path.join(NA, "sheetY_*.xlsx")))[0]
    kx, ux = key(sx)
    ky, uy = key(sy)
    ka = agreed(kx, ky)
    out = ["NEW HELP-DESK APPS: R1 and A/B variants vs LLM answer keys (rule results/new_apps_rule.md)",
           f"key X = Claude Sonnet 5.5 ({os.path.basename(sx)}), key Y = ChatGPT GPT-6 ({os.path.basename(sy)})"]
    # key reliability
    px, py = pairs_same(kx, apps), pairs_same(ky, apps)
    out.append(f"\nKEY AGREEMENT (within-app pairs: {len(px)}): X dup pairs {px.sum()}, Y dup pairs {py.sum()}, both {(px & py).sum()}; "
               f"pair kappa {cohen_kappa_score(px, py):.3f}")
    for a in apps.unique():
        ids = apps.index[apps == a]
        out.append(f"  {a:18s} ARI {adjusted_rand_score(kx[ids], ky[ids]):.3f} | ungrouped X {int(ux[ids].sum())} Y {int(uy[ids].sum())} of {len(ids)}")
    # predictions, all 588
    ref = lambda r: r - 1_000_001                       # harness complaint_ref (offset) -> sheet id
    variants = {
        "R1 app replay (deployed)": app_replay("new_apps", t.index.to_numpy()),
        "V0 R1 (harness)": harness("new_apps", "llm", f"llm_{TAG}_founder_gated_ext_playstore", ref),
        "V1 cosine only": harness("new_apps", "single", f"single_ceA_ceB_{TAG}_ext_playstore", ref),
        "V2 ce_A judge": harness("new_apps", "ceA", f"single_ceA_ceB_{TAG}_ext_playstore", ref),
        "V3 ce_B judge": harness("new_apps", "ceB", f"single_ceA_ceB_{TAG}_ext_playstore", ref),
        "V4 R1 + bi_C retrieval": harness("new_apps", "llm", f"llm_{TAG}_founder_gated_embbi_C_ext_playstore", ref),
        "V5 ce_B + bi_C (no LLM)": harness("new_apps", "ceB", f"ceB_{TAG}_embbi_C_ext_playstore", ref),
    }
    missing = [k for k, v in variants.items() if v is None or len(v) < len(t)]
    variants = {k: v for k, v in variants.items() if k not in missing}
    for nm, lab in (("KEY X (Claude)", kx), ("KEY Y (ChatGPT)", ky), ("AGREED KEY (pairs both keys group)", ka)):
        out += score(f"ALL 588 vs {nm}", variants, lab, apps)
    if missing:
        out.append(f"\n  not yet available for the 588 run: {', '.join(missing)}")
    # Jira-only blind run
    jira = t.index[t["product"] == "Jira Cloud"].to_numpy()
    jref = lambda r: jira[r - 1_000_001]
    jv = {
        "R1 app replay (deployed)": app_replay("new_apps_jira_only", jira),
        "V0 R1 (harness)": harness("jira_new", "llm", f"llm_{TAG}_founder_gated_ext_playstore", jref),
        "V1 cosine only": harness("jira_new", "single", f"single_ceA_ceB_{TAG}_ext_playstore", jref),
        "V2 ce_A judge": harness("jira_new", "ceA", f"single_ceA_ceB_{TAG}_ext_playstore", jref),
        "V3 ce_B judge": harness("jira_new", "ceB", f"single_ceA_ceB_{TAG}_ext_playstore", jref),
        "V4 R1 + bi_C retrieval": harness("jira_new", "llm", f"llm_{TAG}_founder_gated_embbi_C_ext_playstore", jref),
        "V5 ce_B + bi_C (no LLM)": harness("jira_new", "ceB", f"ceB_{TAG}_embbi_C_ext_playstore", jref),
    }
    jv = {k: v for k, v in jv.items() if v is not None and len(v) == len(jira)}
    ja = apps[jira]
    for nm, lab in (("KEY X (Claude)", kx), ("KEY Y (ChatGPT)", ky), ("AGREED KEY", ka)):
        out += score(f"JIRA ONLY (separate blind run, 200) vs {nm}", jv, lab[jira], ja)
    text = "\n".join(out)
    print(text)
    open(os.path.join(RES, "new_apps_scores.txt"), "w", encoding="utf-8").write(text + "\n")


if __name__ == "__main__":
    main()
