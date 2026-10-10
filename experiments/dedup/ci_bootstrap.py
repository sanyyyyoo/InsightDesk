"""
Bootstrap confidence intervals for the frozen dedup results (no LLM calls).

Cluster bootstrap: resample whole true problem groups (issue_id) with
replacement, 2000 times, inside each evaluated partition; a review copied k
times keeps its prediction; pairs between copies of the SAME review are not
counted. Pairwise precision / recall / F1 are pooled over the partitions of a
setting. Differences between methods use the same resamples (paired).

  python experiments/dedup/ci_bootstrap.py
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(__file__))
from spike_grouping import G, RES  # noqa: E402

B, SEED = 2000, 11


def c2(x):
    return x * (x - 1) / 2.0


def load(f, judge, seed, half):
    a = pd.read_csv(os.path.join(RES, f + ".csv"))
    a = a[(a.judge == judge) & (a.split_seed.astype(str) == str(seed)) & (a.held_out_half == half)]
    return a.drop_duplicates("complaint_ref", keep="last").set_index("complaint_ref").case


def counts(case, issue, w_issue):
    """TP, predicted pairs, true pairs with issue weights w (copies), excluding self-copy pairs."""
    w = w_issue[issue]                       # weight of every review
    self_pairs = c2(w)
    df = pd.DataFrame({"case": case, "issue": issue, "w": w, "s": self_pairs})
    cell = df.groupby(["case", "issue"]).agg(N=("w", "sum"), S=("s", "sum"))
    tp = float((c2(cell.N) - cell.S).sum())
    byc = df.groupby("case").agg(N=("w", "sum"), S=("s", "sum"))
    pred = float((c2(byc.N) - byc.S).sum())
    byi = df.groupby("issue").agg(N=("w", "sum"), S=("s", "sum"))
    true = float((c2(byi.N) - byi.S).sum())
    return tp, pred, true


def prf(tp, pred, true):
    p = tp / pred if pred else 0.0
    r = tp / true if true else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)


def run(name, methods, label_of):
    """methods: {method: [Series ref->case per partition]}; same partitions for every method."""
    rng = np.random.default_rng(SEED)
    parts = list(zip(*methods.values()))
    names = list(methods)
    prepared = []
    for per_method in parts:
        refs = per_method[0].index
        issue_codes, issue = np.unique(label_of.reindex(refs).astype(str).to_numpy(), return_inverse=True)
        cases = [m.reindex(refs).to_numpy() for m in per_method]
        prepared.append((issue, len(issue_codes), cases))
    point = {}
    for k, n in enumerate(names):
        tot = np.zeros(3)
        for issue, n_iss, cases in prepared:
            tot += counts(cases[k], issue, np.ones(n_iss))
        point[n] = prf(*tot)
    boot = {n: [] for n in names}
    for _ in range(B):
        tot = {n: np.zeros(3) for n in names}
        for issue, n_iss, cases in prepared:
            w = np.bincount(rng.integers(0, n_iss, n_iss), minlength=n_iss).astype(float)
            for k, n in enumerate(names):
                tot[n] += counts(cases[k], issue, w)
        for n in names:
            boot[n].append(prf(*tot[n]))
    true_pairs = sum(counts(cases[0], issue, np.ones(n_iss))[2] for issue, n_iss, cases in prepared)
    print(f"\n{name}  ({int(true_pairs)} true duplicate pairs, {sum(len(i) for i, _, _ in prepared)} reviews)")
    print(f"  {'method':16s} {'precision':>22s} {'recall':>22s} {'F1':>22s}")
    arr = {n: np.array(boot[n]) for n in names}
    for n in names:
        lo, hi = np.percentile(arr[n], [2.5, 97.5], axis=0)
        cells = [f"{point[n][j]:.3f} [{lo[j]:.3f},{hi[j]:.3f}]" for j in range(3)]
        print(f"  {n:16s} {cells[0]:>22s} {cells[1]:>22s} {cells[2]:>22s}")
    if "R1" in arr:
        for n in names:
            if n == "R1":
                continue
            d = arr[n] - arr["R1"]
            lo, hi = np.percentile(d, [2.5, 97.5], axis=0)
            print(f"  {n} minus R1: precision {point[n][0] - point['R1'][0]:+.3f} [{lo[0]:+.3f},{hi[0]:+.3f}], "
                  f"F1 {point[n][2] - point['R1'][2]:+.3f} [{lo[2]:+.3f},{hi[2]:+.3f}]")
    p_r1 = arr.get("R1")
    if p_r1 is not None:
        print(f"  share of resamples with R1 precision >= 0.85: {(p_r1[:, 0] >= 0.85).mean():.1%}")


def main():
    ps = pd.read_csv("data/external/playstore_scored.csv").set_index("complaint_ref").issue_id
    H = [(0, "A"), (1, "A"), (1, "B")]
    llm = lambda tag: [load(f"playstore_e5_assignments_llm_seeds0_{G}_halfA{tag}_founder_gated" if s == 0
                            else f"playstore_e5_assignments_llm_seeds1_{G}{tag}_founder_gated", "llm", s, h) for s, h in H]
    so = lambda j: [load(f"playstore_e5_assignments_single_oracle_seeds0_{G}_halfA_merge" if s == 0
                         else f"playstore_e5_assignments_single_oracle_seeds1_{G}_merge", j, s, h) for s, h in H]
    run("PLAY STORE, within company (final halves s0A, s1A, s1B)",
        {"R1": llm(""), "R1 + agreement": llm("_top1agree"), "cosine only": so("single"), "oracle": so("oracle")}, ps)

    def lopo(f, j):
        a = pd.read_csv(os.path.join(RES, f + ".csv"))
        return [load(f, j, "lopo", h) for h in sorted(a.held_out_half.unique())]
    run("PLAY STORE, unseen company (leave one company out)",
        {"R1": lopo(f"playstore_e5_assignments_llm_{G}_founder_gated_lopo", "llm"),
         "R1 + agreement": lopo(f"playstore_e5_assignments_llm_{G}_top1agree_founder_gated_lopo", "llm"),
         "cosine only": lopo(f"playstore_e5_assignments_single_oracle_{G}_lopo", "single"),
         "oracle": lopo(f"playstore_e5_assignments_single_oracle_{G}_lopo", "oracle")}, ps)

    for ff in ("firefox", "firefox2", "firefox3"):
        d = pd.read_csv(f"data/external/{ff}.csv")
        lab = pd.Series(d.issue_id.to_numpy(), index=d.complaint_ref + 1_000_000)
        f = f"{ff}_e5_assignments_{{}}_{G}{{}}_ext_playstore"
        run(f"FIREFOX sample {ff[-1] if ff[-1].isdigit() else '1'} (calibrated on Play Store only)",
            {"R1": [load(f.format("llm", "_founder_gated"), "llm", "ext", ff)],
             "cosine only": [load(f.format("single_oracle", ""), "single", "ext", ff)],
             "oracle": [load(f.format("single_oracle", ""), "oracle", "ext", ff)]}, lab)


if __name__ == "__main__":
    main()
