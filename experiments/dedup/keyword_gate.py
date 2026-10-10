"""
Keyword-profile gate on LLM merges (dev half only, no API calls).

Replays the frozen R1 pipeline from its cached judge answers and adds one veto:
an LLM merge is kept only if the new review shares a keyword with the case's
keyword profile (the union of its confirmed members' keywords). Auto-merges
above the band are untouched.

Keywords are unsupervised (KeyBERT's method, no labels, no codebook): candidate
1-2 word phrases from the review (English stop words removed), embedded with
the same MiniLM; the TOP_K phrases closest to the whole review are kept and
their words stemmed.
  hard gate   at least one shared stemmed keyword word
  soft gate   best cosine between any two keyword phrases >= tau

A vetoed merge changes later candidate sets; decisions not in the cache are
counted (cache misses) and treated as "none", so the replay is approximate
when misses are many.

  python experiments/dedup/keyword_gate.py
"""

import collections
import os
import sys

import numpy as np
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer

sys.path.append(os.path.dirname(__file__))

import e5_three_way as e5  # noqa: E402
import stage_attribution as sa  # noqa: E402
from compare_pipelines import evaluate  # noqa: E402
from e5_three_way import band_thresholds_wide, by_group, three_way  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

TOP_K = 5
GENERIC = {"app", "apps", "application"}


def keywords(texts, enc):
    """KeyBERT-style: per review, the TOP_K candidate phrases closest to the review."""
    doc_emb = enc.encode(texts, normalize_embeddings=True, show_progress_bar=False)
    out = []
    for t, d in zip(texts, doc_emb):
        try:
            cv = CountVectorizer(ngram_range=(1, 2), stop_words="english").fit([t])
            cands = [c for c in cv.get_feature_names_out() if not set(c.split()) <= GENERIC]
        except ValueError:
            cands = []
        if not cands:
            out.append(([], np.zeros((0, doc_emb.shape[1]))))
            continue
        ce = enc.encode(cands, normalize_embeddings=True, show_progress_bar=False)
        best = np.argsort(-(ce @ d))[:TOP_K]
        out.append(([cands[i] for i in best], ce[best]))
    return out


class GatedJudge(sa.ReplayJudge):
    def __init__(self, refs, issues, kw, stems, mode, tau=None):
        super().__init__(refs, issues)
        self.kw, self.stems, self.mode, self.tau = kw, stems, mode, tau
        self.vetoed = self.vetoed_correct = 0

    def _ok(self, i, members):
        if self.mode == "none":
            return True
        if self.mode == "hard":
            prof = set().union(*(self.stems[m] for m in members))
            return bool(self.stems[i] & prof)
        a = self.kw[i][1]
        b = np.vstack([self.kw[m][1] for m in members])
        return len(a) > 0 and len(b) > 0 and float((a @ b.T).max()) >= self.tau

    def choose(self, i, candidates, shown=None):
        pick = super().choose(i, candidates, shown)
        if pick >= 0 and not self._ok(i, candidates[pick]):
            self.vetoed += 1
            major = collections.Counter(self.issues[candidates[pick]]).most_common(1)[0][0]
            self.vetoed_correct += int(major == self.issues[i])
            return -1
        return pick


def main():
    from sentence_transformers import SentenceTransformer
    enc = SentenceTransformer(e5.EMBED_MODEL)
    df = apply_text_mode(load_ground_truth(path=DATA_PATHS["playstore"]), "boilerplate", enc)
    emb = enc.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    groups = np.array(df["department"].astype(str).tolist())
    refs = df["complaint_ref"].values
    texts = df["complaint_text"].astype(str).tolist()
    kw = keywords(texts, enc)
    ps = PorterStemmer()
    stems = [{ps.stem(w) for p in k[0] for w in p.split()} for k in kw]
    for r in (0, 1, 2):
        print("example keywords:", texts[r][:70].replace("\n", " "), "->", kw[r][0])

    e5.MAX_CANDIDATES = 5
    ids = np.array(sorted(set(issues)))
    half = set(np.random.default_rng(0).choice(ids, size=len(ids) // 2, replace=False))
    tune = np.where(np.isin(issues, list(half)))[0]
    test = np.where(~np.isin(issues, list(half)))[0]          # dev half = split 0, half B
    t_high, t_low = band_thresholds_wide(emb[tune], issues[tune], groups[tune])

    print(f"\ndev half (split 0 B), band [{t_low:.2f},{t_high:.2f})")
    for mode, tau in (("none", None), ("hard", None), ("soft", 0.5), ("soft", 0.6), ("soft", 0.7)):
        j = GatedJudge(refs, issues, kw, stems, mode, tau)
        labels, _, _ = by_group(lambda r: three_way(emb, r, t_high, t_low, j, True), test, groups)
        m = evaluate(labels, issues[test], np.arange(len(test)))
        name = mode if tau is None else f"{mode} tau={tau}"
        print(f"  {name:13s} P={m['pair_precision']:.3f} R={m['pair_recall']:.3f} F1={m['pair_f1']:.3f} "
              f"contam={m['contaminated_cases']} | merges vetoed {j.vetoed} (of which correct {j.vetoed_correct}) "
              f"| cache misses {j.misses}")


if __name__ == "__main__":
    main()
