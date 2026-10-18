"""
Offline dedup experiment harness (no Supabase, no Pinecone).

Replays the synthetic ground-truth complaints through configurable
variants of the Dedup v1 pipeline and reports the SAME metrics as
scraper/evaluate_threshold_replay.py, plus pairwise clustering
precision / recall / F1 and a retrieval diagnostic.

Baseline (Dedup v1, frozen on data-recalibration):
  clean_text -> MiniLM -> cosine Top-5 over case representatives
  -> STS-B CrossEncoder vs representative text -> merge if >= 0.5858
  Representative = FIRST complaint of the case, frozen.

Variants (one axis changed at a time):
  representation : first | medoid | centroid | multi
  top_k          : 5 | 10 | 20
  threshold      : any
"""

import os
import re
import sys
from dataclasses import dataclass, field
from itertools import combinations

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from backend.services.preprocess import clean_text  # noqa: E402

GROUND_TRUTH_PATH = "data/synthetic_ground_truth.csv"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
CROSS_ENCODER_MODEL_NAME = "cross-encoder/stsb-distilroberta-base"
BASELINE_THRESHOLD = 0.5858
MULTI_REP_MEMBERS = 3


# ==========================================================
# Models (loaded once) + cross-encoder score cache
# ==========================================================

class Models:
    def __init__(self):
        from sentence_transformers import CrossEncoder, SentenceTransformer

        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.cross_encoder = CrossEncoder(CROSS_ENCODER_MODEL_NAME)
        self._ce_cache = {}

    def embed(self, texts):
        vectors = self.embedder.encode(
            list(texts), batch_size=64, show_progress_bar=False
        )
        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        return vectors / np.where(norms == 0, 1e-12, norms)

    def ce_scores(self, query, texts):
        """Cross-encoder scores for (query, text) pairs, cached."""
        missing = [t for t in texts if (query, t) not in self._ce_cache]

        if missing:
            scores = self.cross_encoder.predict(
                [[query, t] for t in missing], show_progress_bar=False
            )
            for t, s in zip(missing, scores):
                self._ce_cache[(query, t)] = float(s)

        return [self._ce_cache[(query, t)] for t in texts]


# ==========================================================
# Data
# ==========================================================

# Stock phrases the synthetic generator attaches to complaints of ANY
# issue. They are an artefact of the evaluation data (real customers do
# not share these exact sentences), so removing them is a data fix for
# evaluation only - never part of the production pipeline.
GENERATOR_OPENERS = re.compile(
    r"^(Reporting this again|Update|Following up on this|"
    r"Just ran into this once more|Still happening|This has come up again)"
    r"\s*[:\-.]\s*",
    re.IGNORECASE,
)
GENERATOR_CLOSERS = re.compile(
    r"\s*(Happening consistently, not a one-off\.|This is affecting my daily work\.|"
    r"Please look into this soon\.|Can someone confirm this is being looked at\?)\s*$",
    re.IGNORECASE,
)


def strip_generator_templates(text):
    text = GENERATOR_OPENERS.sub("", text.strip())
    for _ in range(2):
        text = GENERATOR_CLOSERS.sub("", text)
    return text.strip()


def load_ground_truth(path=GROUND_TRUTH_PATH, order_seed=None, strip_templates=False):
    df = pd.read_csv(path)
    df = df.sort_values("complaint_ref", kind="stable").reset_index(drop=True)

    if order_seed is not None:
        df = df.sample(frac=1.0, random_state=order_seed).reset_index(drop=True)

    text = df["complaint_text"].astype(str)
    if strip_templates:
        text = text.map(strip_generator_templates)

    df["cleaned_text"] = text.map(clean_text)
    return df


# ==========================================================
# Case pool
# ==========================================================

@dataclass
class Case:
    index: int
    member_rows: list = field(default_factory=list)
    rep_row: int = -1              # row used as representative text
    centroid: np.ndarray = None    # normalised mean member embedding


class Replay:
    def __init__(self, df, emb, models, representation="first", top_k=5,
                 threshold=BASELINE_THRESHOLD):
        assert representation in {"first", "medoid", "centroid", "multi"}
        self.df, self.emb, self.models = df, emb, models
        self.representation = representation
        self.top_k = top_k
        self.threshold = threshold
        self.cases = []
        self.case_of_row = {}
        self.log = []

    # ---------- representatives ----------

    def _update_representative(self, case):
        rows = case.member_rows
        vectors = self.emb[rows]
        mean = vectors.mean(axis=0)
        case.centroid = mean / max(np.linalg.norm(mean), 1e-12)

        if self.representation == "first":
            case.rep_row = rows[0]
        else:
            # Medoid: member with the highest mean cosine to the others
            # (for 1-2 members this is the first member).
            if len(rows) <= 2:
                case.rep_row = rows[0]
            else:
                sims = vectors @ vectors.T
                case.rep_row = rows[int(np.argmax(sims.mean(axis=1)))]

    def _retrieval_vectors(self):
        """One vector per case (for first/medoid/centroid)."""
        if self.representation == "centroid":
            return np.stack([c.centroid for c in self.cases])
        return self.emb[[c.rep_row for c in self.cases]]

    # ---------- retrieval ----------

    def _candidates(self, row):
        q = self.emb[row]

        if self.representation == "multi":
            # Score each case by its best-matching member.
            case_scores = np.array([
                float(np.max(self.emb[c.member_rows] @ q)) for c in self.cases
            ])
        else:
            case_scores = self._retrieval_vectors() @ q

        order = np.argsort(case_scores)[::-1][: self.top_k]
        return [int(i) for i in order], case_scores

    # ---------- rerank ----------

    def _rerank(self, row, candidate_ids):
        query = self.df.at[row, "cleaned_text"]
        best_case, best_score = None, -np.inf

        for cid in candidate_ids:
            case = self.cases[cid]

            if self.representation == "multi":
                # Compare with the case's M members closest to the query.
                members = case.member_rows
                sims = self.emb[members] @ self.emb[row]
                picked = [members[i] for i in np.argsort(sims)[::-1][:MULTI_REP_MEMBERS]]
                texts = [self.df.at[r, "cleaned_text"] for r in picked]
                score = max(self.models.ce_scores(query, texts))
            else:
                text = self.df.at[case.rep_row, "cleaned_text"]
                score = self.models.ce_scores(query, [text])[0]

            if score > best_score:
                best_case, best_score = cid, score

        return best_case, best_score

    # ---------- main loop ----------

    def run(self):
        issues = self.df["issue_id"].astype(str).values

        for row in range(len(self.df)):
            decision, score, cand_ids = "new_case", None, []
            correct_case_exists = correct_in_candidates = False

            if self.cases:
                cand_ids, _ = self._candidates(row)
                best_case, score = self._rerank(row, cand_ids)

                # Diagnostic: does a case of this complaint's issue exist,
                # and did retrieval surface one?
                issue = issues[row]
                issue_cases = {
                    c.index for c in self.cases
                    if any(issues[r] == issue for r in c.member_rows)
                }
                correct_case_exists = bool(issue_cases)
                correct_in_candidates = bool(issue_cases & set(cand_ids))

                if score >= self.threshold:
                    decision = "merge"
                    case = self.cases[best_case]
                    case.member_rows.append(row)
                    self._update_representative(case)
                    self.case_of_row[row] = best_case

            if decision == "new_case":
                case = Case(index=len(self.cases), member_rows=[row])
                self._update_representative(case)
                self.cases.append(case)
                self.case_of_row[row] = case.index

            self.log.append({
                "row": row,
                "issue_id": issues[row],
                "decision": decision,
                "score": score,
                "correct_case_exists": correct_case_exists,
                "correct_in_candidates": correct_in_candidates,
                "merged_into_right_issue": (
                    decision == "merge"
                    and self._majority_issue(self.case_of_row[row], exclude=row) == issues[row]
                ),
            })

        return self

    def _majority_issue(self, case_index, exclude=None):
        issues = self.df["issue_id"].astype(str).values
        rows = [r for r in self.cases[case_index].member_rows if r != exclude]
        if not rows:
            return None
        values, counts = np.unique(issues[rows], return_counts=True)
        return values[int(np.argmax(counts))]


# ==========================================================
# Metrics (same definitions as evaluate_threshold_replay.py)
# ==========================================================

def case_metrics(replay):
    df = replay.df
    issues = df["issue_id"].astype(str).values
    issue_totals = df.groupby("issue_id").size().to_dict()

    contaminated = pure = cross_issue = 0
    issue_case_counts = {}

    for case in replay.cases:
        counts = {}
        for r in case.member_rows:
            counts[issues[r]] = counts.get(issues[r], 0) + 1
            issue_case_counts.setdefault(issues[r], {})
            issue_case_counts[issues[r]][case.index] = issue_case_counts[issues[r]].get(case.index, 0) + 1

        if len(counts) > 1:
            contaminated += 1
            cross_issue += len(case.member_rows) - max(counts.values())
        else:
            pure += 1

    n_cases = len(replay.cases)
    cases_per_issue = [len(v) for v in issue_case_counts.values()]
    coverage = [max(v.values()) / issue_totals[k] for k, v in issue_case_counts.items()]

    # Pairwise clustering precision/recall over all complaint pairs.
    same_case = same_issue = both = 0
    case_ids = np.array([replay.case_of_row[r] for r in range(len(df))])
    for a, b in combinations(range(len(df)), 2):
        sc = case_ids[a] == case_ids[b]
        si = issues[a] == issues[b]
        same_case += sc
        same_issue += si
        both += sc and si
    p = both / same_case if same_case else 0.0
    r = both / same_issue if same_issue else 0.0

    log = pd.DataFrame(replay.log)
    has_case = log[log.correct_case_exists]

    return {
        "final_cases": n_cases,
        "mean_cases_per_issue": float(np.mean(cases_per_issue)),
        "mean_largest_case_coverage": float(np.mean(coverage)),
        "contaminated_cases": contaminated,
        "contaminated_case_rate": contaminated / n_cases,
        "pure_case_rate": pure / n_cases,
        "cross_issue_assignments": cross_issue,
        "pair_precision": p,
        "pair_recall": r,
        "pair_f1": 2 * p * r / (p + r) if p + r else 0.0,
        "retrieval_recall": float(has_case.correct_in_candidates.mean()) if len(has_case) else np.nan,
        "merges": int((log.decision == "merge").sum()),
        "wrong_issue_merges": int(((log.decision == "merge") & ~log.merged_into_right_issue).sum()),
    }
