"""
Worked example + confidence intervals, printed step by step from the real
code (no hand-typed numbers).

PART 1  eight real synthetic complaints through every calculation:
        boilerplate rule, cleaning, embeddings, cosine (by hand and by
        library), STS-B scores, v1 and v2 decisions complaint by complaint,
        all 28 pairs -> TP/FP/FN -> P/R/F1, band thresholds (t_high/t_low)
        from a real tuning half, AUC by counting, z-score, batch linkage.
PART 2  how strongly the main claims hold: bootstrap / t / Wilson 95% CIs.

  python experiments/dedup/worked_example.py > results/worked_example.txt
"""

import itertools
import os
import sys

import numpy as np
import pandas as pd
from scipy.cluster.hierarchy import fcluster, linkage
from scipy.spatial.distance import pdist
from sklearn.metrics import roc_auc_score
from sklearn.metrics.cluster import pair_confusion_matrix

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402
from compare_pipelines import online_cos  # noqa: E402
from normalize import boilerplate_suppress  # noqa: E402
from replay_lab import Models, Replay, load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
RNG = np.random.default_rng(12345)
PICK = [("login_otp_not_received", 3), ("dashboard_extremely_slow", 2), ("session_logs_out_randomly", 2), ("sso_login_fails", 1)]


def hr(title):
    print("\n" + "=" * 100 + f"\n{title}\n" + "=" * 100)


def prf(tp, fp, fn):
    p = tp / (tp + fp) if tp + fp else 1.0
    r = tp / (tp + fn) if tp + fn else 0.0
    f = 2 * p * r / (p + r) if p + r else 0.0
    return p, r, f


def main():
    np.set_printoptions(precision=3, suppress=True, linewidth=140)
    models = Models()
    enc = models.embedder
    df = load_ground_truth()
    raw_all = df["complaint_text"].astype(str).tolist()

    # ------------------------------------------------------------------ sample
    rows = []
    for issue, k in PICK:
        rows += df.index[df.issue_id == issue][:k].tolist()
    rows = sorted(rows)                                     # arrival order
    S = df.loc[rows].reset_index(drop=True)
    names = [f"C{i + 1}" for i in range(len(S))]
    hr("PART 1 · STEP 0 · the sample: 8 real complaints from data/synthetic_ground_truth.csv, in arrival order")
    for n, (_, r) in zip(names, S.iterrows()):
        print(f"{n}  issue={r.issue_id:28s} ref={r.complaint_ref:4d}  {r.complaint_text}")

    # ------------------------------------------------------------------ boilerplate
    hr("STEP 1 · boilerplate rule (learned from all 488 complaints; no labels, no phrase list)")
    print("A sentence is filler if (a) near-copies (cosine >= 0.90) occur in >= 8 complaints AND\n"
          "(b) those complaints are otherwise unrelated: cohesion of their remaining text <= 0.30, where\n"
          "    cohesion = ( sum_i sum_j cos(rest_i, rest_j) - n ) / ( n (n - 1) )   (mean over the n(n-1) off-diagonal pairs)")
    bp_all, report = boilerplate_suppress(raw_all, enc, return_report=True)
    dropped = {s.lower().strip(): (h, c) for s, h, c, d in report if d}
    bp = [bp_all[i] for i in rows]
    for n, r, b in zip(names, S.complaint_text, bp):
        print(f"{n}: {r!r}\n    -> {b!r}")
    shown = set()
    for r in S.complaint_text:
        for seg, (h, c) in dropped.items():
            if seg in r.lower() and seg not in shown:
                shown.add(seg)
                print(f"   dropped segment {seg!r}: found in {h} complaints, rest cohesion {c:.3f} <= 0.30")

    # worked cohesion for one dropped segment
    seg = next(iter(shown))
    segs_emb = enc.encode([seg], normalize_embeddings=True)
    host_idx = [i for i, t in enumerate(raw_all) if seg in t.lower()]
    print(f"\n  Worked cohesion for {seg!r} (exact-substring hosts only, for illustration; the rule also counts near-copies):")
    rest = [clean_text(bp_all[i]) for i in host_idx]
    R = enc.encode(rest, normalize_embeddings=True)
    M = R @ R.T
    n = len(R)
    print(f"   n = {n} complaints, sum of all n x n cosines = {M.sum():.3f}, diagonal (self) = n = {n}")
    print(f"   cohesion = ({M.sum():.3f} - {n}) / ({n} x {n - 1}) = {(M.sum() - n) / (n * (n - 1)):.3f}")
    _ = segs_emb

    # ------------------------------------------------------------------ cleaning + embeddings
    hr("STEP 2 · clean_text (production preprocessing) and MiniLM embeddings")
    clean_v2 = [clean_text(t) for t in bp]
    clean_v1 = [clean_text(t) for t in S.complaint_text]
    for n, a, b in zip(names, clean_v1, clean_v2):
        print(f"{n}: v1 text: {a!r}\n    v2 text: {b!r}")
    E = enc.encode(clean_v2, normalize_embeddings=True)
    E1 = enc.encode(clean_v1, normalize_embeddings=True)
    print(f"\nEach vector has {E.shape[1]} numbers and length 1 (|C1| = {np.linalg.norm(E[0]):.6f}).")
    print(f"C1 first 5 numbers: {E[0][:5]}")
    a, b = 0, 1
    prod = E[a] * E[b]
    print(f"\nCosine by hand, C1 vs C2 (v2 text):  cos = sum_k C1[k]*C2[k] / (|C1| |C2|)")
    print(f"   first 5 products: {prod[:5]}  ... (384 products)")
    print(f"   sum of all 384 products = {prod.sum():.6f};  |C1||C2| = {np.linalg.norm(E[a]) * np.linalg.norm(E[b]):.6f}")
    print(f"   cos(C1,C2) = {prod.sum():.4f}")

    # ------------------------------------------------------------------ cosine + STS-B matrices
    hr("STEP 3 · cosine matrix (v2 text) and STS-B cross-encoder scores (v1 text)")
    C = E @ E.T
    print(pd.DataFrame(C, index=names, columns=names).round(3).to_string())
    ce = np.zeros((len(S), len(S)))
    for i, j in itertools.combinations(range(len(S)), 2):
        ce[i, j] = ce[j, i] = models.ce_scores(clean_v1[i], [clean_v1[j]])[0]
    print("\nSTS-B scores (v1 decision score, 0..1):")
    print(pd.DataFrame(ce, index=names, columns=names).round(3).to_string())

    # ------------------------------------------------------------------ v1 and v2 decisions
    hr("STEP 4 · decisions, complaint by complaint")
    print("v1: MiniLM top-5 founders (v1 text) -> STS-B vs each founder -> merge if best >= 0.6469")
    founders, lab_v1 = [], []
    for i in range(len(S)):
        if founders:
            sims = {f: float(E1[i] @ E1[f]) for f in founders}
            top = sorted(sims, key=sims.get, reverse=True)[:5]
            scores = {f: ce[i, f] for f in top}
            best = max(scores, key=scores.get)
            line = ", ".join(f"{names[f]}:{scores[f]:.3f}" for f in top)
            if scores[best] >= 0.6469:
                lab_v1.append(lab_v1[best])
                print(f"  {names[i]}: STS-B vs founders [{line}] -> best {scores[best]:.3f} >= 0.6469 -> MERGE into case of {names[best]}")
                continue
            print(f"  {names[i]}: STS-B vs founders [{line}] -> best {scores[best]:.3f} <  0.6469 -> NEW case")
        else:
            print(f"  {names[i]}: no cases yet -> NEW case")
        founders.append(i)
        lab_v1.append(i)
    print("\nv2: cosine (v2 text) vs each founder -> merge if best >= 0.44 (median held-out threshold)")
    founders, lab_v2 = [], []
    for i in range(len(S)):
        if founders:
            sims = {f: float(C[i, f]) for f in founders}
            best = max(sims, key=sims.get)
            line = ", ".join(f"{names[f]}:{sims[f]:.3f}" for f in founders)
            if sims[best] >= 0.44:
                lab_v2.append(lab_v2[best])
                print(f"  {names[i]}: cosine vs founders [{line}] -> best {sims[best]:.3f} >= 0.44 -> MERGE into case of {names[best]}")
                continue
            print(f"  {names[i]}: cosine vs founders [{line}] -> best {sims[best]:.3f} <  0.44 -> NEW case")
        else:
            print(f"  {names[i]}: no cases yet -> NEW case")
        founders.append(i)
        lab_v2.append(i)
    assert list(online_cos(E, 0.44)) == [sorted(set(lab_v2)).index(x) for x in lab_v2], "hand loop must equal pipeline code"
    print("  (check: identical to compare_pipelines.online_cos)")

    # ------------------------------------------------------------------ pairs
    hr("STEP 5 · all 8x7/2 = 28 pairs -> TP / FP / FN -> precision, recall, F1")
    iss = S.issue_id.values
    print(f"{'pair':8s}{'same issue':>11s}{'v1 same case':>14s}{'v1':>5s}{'v2 same case':>14s}{'v2':>5s}")
    cnt = {"v1": {"TP": 0, "FP": 0, "FN": 0}, "v2": {"TP": 0, "FP": 0, "FN": 0}}
    for i, j in itertools.combinations(range(len(S)), 2):
        truth = iss[i] == iss[j]
        out = []
        for key, lab in (("v1", lab_v1), ("v2", lab_v2)):
            same = lab[i] == lab[j]
            kind = "TP" if same and truth else "FP" if same else "FN" if truth else "TN"
            if kind != "TN":
                cnt[key][kind] += 1
            out += [str(same), kind]
        print(f"{names[i]}-{names[j]:5s}{str(truth):>11s}{out[0]:>14s}{out[1]:>5s}{out[2]:>14s}{out[3]:>5s}")
    for key in ("v1", "v2"):
        tp, fp, fn = cnt[key]["TP"], cnt[key]["FP"], cnt[key]["FN"]
        p, r, f = prf(tp, fp, fn)
        print(f"\n{key}: TP={tp} FP={fp} FN={fn}")
        print(f"   precision = TP/(TP+FP) = {tp}/{tp + fp} = {p:.3f}")
        print(f"   recall    = TP/(TP+FN) = {tp}/{tp + fn} = {r:.3f}")
        print(f"   F1 = 2PR/(P+R) = 2 x {p:.3f} x {r:.3f} / ({p:.3f}+{r:.3f}) = {f:.3f}")
        (tn, fp2), (fn2, tp2) = pair_confusion_matrix(iss, np.array(lab_v1 if key == "v1" else lab_v2)) // 2
        assert (tp2, fp2, fn2) == (tp, fp, fn)
    print("   (check: identical counts from scikit-learn pair_confusion_matrix)")

    # ------------------------------------------------------------------ band thresholds
    hr("STEP 6 · uncertain band from a real tuning half (split seed 0, tune on half A, boilerplate text)")
    full_bp = [clean_text(t) for t in bp_all]
    EF = enc.encode(full_bp, normalize_embeddings=True)
    issues = np.array(df.issue_id.astype(str).tolist())
    ids = np.array(sorted(set(issues)))
    half = set(np.random.default_rng(0).choice(ids, size=len(ids) // 2, replace=False))
    tune = np.where(np.isin(issues, list(half)))[0]
    T = EF[tune] @ EF[tune].T
    iu = np.triu_indices(len(tune), 1)
    s, same = T[iu], (issues[tune][:, None] == issues[tune][None, :])[iu]
    order = np.argsort(-s)
    cum_tp = np.cumsum(same[order])
    prec = cum_tp / np.arange(1, len(order) + 1)
    ok = np.where(prec >= 0.97)[0]
    k = ok.max()
    print(f"tuning half: {len(tune)} complaints -> {len(s)} pairs, {int(same.sum())} of them true duplicates")
    print("t_high = lowest cosine t such that precision of {pairs with cosine >= t} >= 0.97")
    for j in sorted(set([max(0, k - 2), k, min(len(order) - 1, k + 1), min(len(order) - 1, k + 50)])):
        print(f"   pairs with cos >= {s[order][j]:.4f}: {j + 1:5d} pairs, {int(cum_tp[j]):5d} duplicates -> precision {prec[j]:.4f}")
    t_high = float(s[order][k])
    print(f"   -> t_high = {t_high:.4f}")
    print("t_low: walk down from t_high in 0.02 bins; stop at the first bin where < 20% of pairs are duplicates")
    t_low = t_high
    while t_low - 0.02 > 0:
        m = (s >= t_low - 0.02) & (s < t_low)
        share = same[m].mean() if m.any() else float("nan")
        print(f"   bin [{t_low - 0.02:.3f}, {t_low:.3f}): {int(m.sum()):5d} pairs, {int(same[m].sum()):4d} duplicates -> share {share:.3f}")
        if m.any() and share < 0.20:
            break
        t_low -= 0.02
    print(f"   -> t_low = {t_low:.4f}   band = [{t_low:.3f}, {t_high:.3f})")
    print("Three-way decision for our sample with this band:")
    for i in range(1, len(S)):
        best = max(C[i, :i])
        d = "MERGE (auto)" if best >= t_high else "NEW case" if best < t_low else "REVIEW QUEUE"
        print(f"   {names[i]}: best cosine to an earlier complaint {best:.3f} -> {d}")

    # ------------------------------------------------------------------ AUC by counting
    hr("STEP 7 · ROC AUC by counting (150 calibration pairs, same pairs for every scorer)")
    pairs = pd.read_csv("data/calibration_pairs.csv")
    y = (pairs.true_label == "duplicate").values
    A = enc.encode(pairs.text_a.astype(str).map(clean_text).tolist(), normalize_embeddings=True)
    B = enc.encode(pairs.text_b.astype(str).map(clean_text).tolist(), normalize_embeddings=True)
    cos150 = (A * B).sum(1)
    sts150 = np.array([models.ce_scores(clean_text(x), [clean_text(z)])[0] for x, z in zip(pairs.text_a, pairs.text_b)])
    for name, sc in (("MiniLM cosine", cos150), ("STS-B", sts150)):
        pos, neg = sc[y], sc[~y]
        wins = sum((p > q) + 0.5 * (p == q) for p in pos for q in neg)
        print(f"{name}: {len(pos)} duplicates x {len(neg)} non-duplicates = {len(pos) * len(neg)} comparisons; "
              f"duplicate scored higher in {wins:.1f} -> AUC = {wins:.1f}/{len(pos) * len(neg)} = {wins / (len(pos) * len(neg)):.4f}"
              f"   (sklearn: {roc_auc_score(y, sc):.4f})")

    # ------------------------------------------------------------------ z-score
    hr("STEP 8 · spike z-score (backend/services/spike_detection.py) on an example window history")
    hist = [2, 1, 3, 2, 2, 1]
    cur = 9
    mu, sd = np.mean(hist), np.std(hist)
    print(f"previous 6-h windows {hist}, current window {cur}  (needs >= 7 windows in total)")
    print(f"   mean = {sum(hist)}/{len(hist)} = {mu:.4f}")
    print(f"   std (population) = sqrt( sum (x-mean)^2 / n ) = sqrt({sum((x - mu) ** 2 for x in hist):.4f}/{len(hist)}) = {sd:.4f}")
    print(f"   z = (current - mean)/std = ({cur} - {mu:.4f})/{sd:.4f} = {(cur - mu) / sd:.2f}  -> spike if > 2, critical if > 3")

    # ------------------------------------------------------------------ batch linkage
    hr("STEP 9 · batch average-linkage on the 8 (distance = 1 - cosine), cut at t = 0.44")
    Z = linkage(pdist(E, metric="cosine"), method="average")
    clusters = {i: [names[i]] for i in range(len(S))}
    for step, (x, y_, dist, size) in enumerate(Z):
        x, y_ = int(x), int(y_)
        new = clusters.pop(x) + clusters.pop(y_)
        clusters[len(S) + step] = new
        print(f"   merge {new} at average distance {dist:.3f} (= average cosine {1 - dist:.3f})"
              + ("" if dist <= 1 - 0.44 else "   <- above 1-0.44 = 0.56: not merged in the final cut"))
    lab_b = fcluster(Z, t=1 - 0.44, criterion="distance")
    print(f"   final groups at cut 0.56: {[[names[i] for i in range(len(S)) if lab_b[i] == c] for c in sorted(set(lab_b))]}")

    # ================================================================== PART 2
    hr("PART 2 · how strongly the main results hold (95% confidence intervals)")
    # C1 paired bootstrap on AUC
    B_ = 2000
    d, ac, asb = [], [], []
    idx = np.arange(len(y))
    for _ in range(B_):
        b_ = RNG.choice(idx, size=len(idx), replace=True)
        if y[b_].all() or (~y[b_]).all():
            continue
        c1, c2 = roc_auc_score(y[b_], cos150[b_]), roc_auc_score(y[b_], sts150[b_])
        ac.append(c1)
        asb.append(c2)
        d.append(c1 - c2)
    ci = lambda v: (np.percentile(v, 2.5), np.percentile(v, 97.5))  # noqa: E731
    print(f"C1  AUC, paired bootstrap over the 150 pairs ({len(d)} resamples):")
    print(f"    cosine {roc_auc_score(y, cos150):.3f} [{ci(ac)[0]:.3f}, {ci(ac)[1]:.3f}]   STS-B {roc_auc_score(y, sts150):.3f} "
          f"[{ci(asb)[0]:.3f}, {ci(asb)[1]:.3f}]   difference {roc_auc_score(y, cos150) - roc_auc_score(y, sts150):+.3f} "
          f"[{ci(d)[0]:+.3f}, {ci(d)[1]:+.3f}]   share of resamples where cosine wins: {np.mean(np.array(d) > 0):.3f}")

    # C2 paired held-out runs
    raw = pd.read_csv(os.path.join(RESULTS, "pipelines_all-MiniLM-L6-v2.csv"))
    bpf = pd.read_csv(os.path.join(RESULTS, "pipelines_all-MiniLM-L6-v2_boilerplate.csv"))
    llm = pd.read_csv(os.path.join(RESULTS, "pipelines_all-MiniLM-L6-v2_llm.csv"))
    v1 = raw[raw.pipeline.str.startswith("v1")].pair_f1.values
    v2 = bpf[bpf.pipeline.str.startswith("online")].pair_f1.values
    l2 = llm[llm.pipeline.str.startswith("online")].pair_f1.values

    def tci(diff, label):
        m, sdv, n_ = diff.mean(), diff.std(ddof=1), len(diff)
        h = 2.262 * sdv / np.sqrt(n_)                    # t(0.975, df=9) = 2.262
        print(f"C2  {label}: per-run differences {np.round(diff, 3).tolist()}")
        print(f"    mean {m:+.3f}, sd {sdv:.3f}, 95% CI = mean +/- 2.262 x sd/sqrt(10) = [{m - h:+.3f}, {m + h:+.3f}]; "
              f"positive in {int((diff > 0).sum())}/10 runs")
    tci(v2 - v1, "held-out F1, v2 (boilerplate+cosine, online) minus v1 (STS-B), same 10 splits")
    tci(l2 - v2, "held-out F1, LLM text minus no-LLM (both online cosine), same 10 splits")
    print("    note: the 10 runs reuse the same 488 complaints, so they are not fully independent; treat the t-interval as optimistic.")

    # C3 cluster bootstrap over issues on the full 1,432 replay
    from full_replay import load, score
    full = load()
    fe = models.embed(full["cleaned_text"])
    models._ce_cache = {}
    rep = Replay(full, fe, models, "first", 5, 0.6469).run()
    lab1 = np.array([rep.case_of_row[r] for r in range(len(full))])
    bpf_all = [clean_text(t) for t in boilerplate_suppress(full["complaint_text"].astype(str).tolist(), enc)]
    lab2 = online_cos(enc.encode(bpf_all, normalize_embeddings=True), 0.44)
    s1, s2 = score(full, {i: int(c) for i, c in enumerate(lab1)}, "v1"), score(full, {i: int(c) for i, c in enumerate(lab2)}, "v2")
    print(f"C3  full 1,432 replay (point estimates): v1 STS-B 0.6469 P={s1['pair_precision']:.3f} R={s1['pair_recall']:.3f} F1={s1['pair_f1']:.3f} | "
          f"v2 P={s2['pair_precision']:.3f} R={s2['pair_recall']:.3f} F1={s2['pair_f1']:.3f}")
    lab_mask = full["labelled"].values
    iss_full = np.array(full.issue_id.astype(str).tolist())
    issue_list = sorted(set(iss_full[lab_mask]))
    K = len(issue_list)

    def per_issue(lab):
        """TP_i, FN_i per issue and FP_ij per issue pair, from the fixed assignments."""
        tp_i, fn_i, fp_ij = np.zeros(K), np.zeros(K), np.zeros((K, K))
        members = [np.where((iss_full == i) & lab_mask)[0] for i in issue_list]
        for a_, ra in enumerate(members):
            la = lab[ra]
            same = sum((la[x] == la[y_]) for x, y_ in itertools.combinations(range(len(la)), 2))
            tp_i[a_] = same
            fn_i[a_] = len(la) * (len(la) - 1) / 2 - same
            for b2 in range(a_ + 1, K):
                lb = lab[members[b2]]
                fp_ij[a_, b2] = fp_ij[b2, a_] = sum(int(np.sum(lb == c)) for c in la)
        return tp_i, fn_i, fp_ij

    stats = [per_issue(lab1), per_issue(lab2)]
    for (tp_i, fn_i, fp_ij), s_ in zip(stats, (s1, s2)):          # consistency with the full-data score
        assert int(tp_i.sum()) == s_["TP"] and int(fn_i.sum()) == s_["FN"] and int(fp_ij.sum() / 2) == s_["FP"]
    print("    (check: per-issue TP/FN/FP sum exactly to the full-data counts)")
    diffs, f1a, f1b, pa, pb = [], [], [], [], []
    for _ in range(1000):
        m = np.bincount(RNG.integers(0, K, size=K), minlength=K).astype(float)   # times each issue is drawn
        res = []
        for tp_i, fn_i, fp_ij in stats:
            tp = (m * tp_i).sum()
            fn = (m * fn_i).sum()
            fp = (np.outer(m, m) * fp_ij).sum() / 2      # pairs between two DIFFERENT drawn issues
            res.append(prf(tp, fp, fn))
        pa.append(res[0][0]); pb.append(res[1][0]); f1a.append(res[0][2]); f1b.append(res[1][2])
        diffs.append(res[1][2] - res[0][2])
    print(f"    issue-level bootstrap (1000 resamples of the 32 issues): F1 v1 [{ci(f1a)[0]:.3f}, {ci(f1a)[1]:.3f}], "
          f"v2 [{ci(f1b)[0]:.3f}, {ci(f1b)[1]:.3f}], difference v2-v1 [{ci(diffs)[0]:+.3f}, {ci(diffs)[1]:+.3f}]")
    print(f"    precision v1 [{ci(pa)[0]:.3f}, {ci(pa)[1]:.3f}]  v2 [{ci(pb)[0]:.3f}, {ci(pb)[1]:.3f}]; "
          f"v2 F1 higher in {np.mean(np.array(diffs) > 0):.3f} of resamples")

    # C4 Wilson intervals for hand checks
    def wilson(k_, n_):
        z = 1.96
        p_ = k_ / n_
        den = 1 + z * z / n_
        cen = (p_ + z * z / (2 * n_)) / den
        half_ = z * np.sqrt(p_ * (1 - p_) / n_ + z * z / (4 * n_ * n_)) / den
        return p_, cen - half_, cen + half_
    for label, k_, n_ in (("real mixed v2 cases judged wrong", 13, 33), ("GitBugs top-30 cross-group pairs judged same bug", 2, 30)):
        p_, lo, hi = wilson(k_, n_)
        print(f"C4  {label}: {k_}/{n_} = {p_:.3f}, Wilson 95% CI [{lo:.3f}, {hi:.3f}]")


if __name__ == "__main__":
    main()
