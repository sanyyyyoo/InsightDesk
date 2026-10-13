"""
E5: three-way dedup decision with a judge for the uncertain band.

Online assignment (first complaint = case representative), cosine on
MiniLM embeddings of the E4a boilerplate-suppressed text:

    best cosine >= t_high          -> merge automatically
    best cosine <  t_low           -> new case
    t_low <= best cosine < t_high  -> JUDGE looks at up to 3 candidate
                                      cases (cosine >= t_low, best first)
                                      and merges into the first "same"

Judges compared:
    single   no band: one threshold t* (the E4 online-cos baseline)
    oracle   a perfect operator (ground-truth issue) = review-queue ceiling
    ce       small cross-encoder fine-tuned ONLY on pairs from the tuning
             half's issues (no LLM)
    llm      Groq LLM judge (cached; run with --judges llm)

Protocol as E2-E4: 5 splits x 2 halves; t*, t_high, t_low and the CE are
all fitted on the tuning half, scored on the held-out half.

  t_high = lowest cosine at which tuning-half pairs are >= 97% same-issue
  t_low  = walking down from t_high in 0.02 bins, the first bin where fewer
           than 20% of tuning-half pairs are same-issue

  python experiments/dedup/e5_three_way.py --judges single oracle ce
"""

import argparse
import json
import os
import random
import re
import sys
import time

import numpy as np
import pandas as pd
import torch

sys.path.append(os.path.dirname(__file__))

from compare_pipelines import evaluate, online_cos, pick_threshold  # noqa: E402
from normalize import DATA_PATHS, apply_text_mode, boilerplate_suppress  # noqa: E402
from replay_lab import load_ground_truth  # noqa: E402

RESULTS = os.path.join(os.path.dirname(__file__), "results")
LLM_CACHE = os.path.join(RESULTS, "llm_judge_cache.jsonl")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
CE_BASE = "cross-encoder/ms-marco-MiniLM-L6-v2"
PRE_GATE = False     # decoupled gate, set from --pre-gate
SECOND_LOOK = ""     # vague second look, set from --second-look ("", "any", "top1")
TRAINED_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "data", "external", "training")
SPLIT_SEEDS = [0, 1, 2, 3, 4]
HIGH_PRECISION = 0.97
LOW_SHARE = 0.20
BIN = 0.02
MAX_CANDIDATES = 3
EXT_REF_OFFSET = 1_000_000   # refs of an external test set, to keep them apart from calibration refs
FEWSHOT_PATH = ""
REQUIRE_TOP1 = False   # merge only when the LLM picks the top-cosine candidate


# ==========================================================
# Band thresholds from the tuning half
# ==========================================================

def band_thresholds(emb, issues, groups=None):
    sims = emb @ emb.T
    iu = np.triu_indices(len(emb), 1)
    s, same = sims[iu], (issues[:, None] == issues[None, :])[iu]
    if groups is not None:                       # per-product: only pairs a company would see
        keep = (groups[:, None] == groups[None, :])[iu]
        s, same = s[keep], same[keep]
    order = np.argsort(-s)
    precision = np.cumsum(same[order]) / np.arange(1, len(order) + 1)
    ok = np.where(precision >= HIGH_PRECISION)[0]
    t_high = float(s[order][ok.max()]) if len(ok) else 0.99

    # Walk down from t_high in 0.02 bins while pairs in the bin are still
    # at least LOW_SHARE same-issue; below that, a candidate is rarely a duplicate.
    t_low = t_high
    while t_low - BIN > 0:
        in_bin = (s >= t_low - BIN) & (s < t_low)
        if in_bin.sum() and same[in_bin].mean() < LOW_SHARE:
            break
        t_low -= BIN
    return t_high, round(t_low, 4)


WIDE_RECALL = 0.80   # wide band: t_low keeps this share of tuning-half duplicate pairs


def band_thresholds_wide(emb, issues, groups=None):
    """Recall-oriented band for real data: t_high as before (pairs above it are
    >= 97% duplicates on the tuning half); t_low = the cosine above which 80% of
    the tuning half's duplicate pairs lie. Everything in between goes to the judge."""
    t_high, _ = band_thresholds(emb, issues, groups)
    sims = emb @ emb.T
    iu = np.triu_indices(len(emb), 1)
    s, same = sims[iu], (issues[:, None] == issues[None, :])[iu]
    if groups is not None:
        keep = (groups[:, None] == groups[None, :])[iu]
        s, same = s[keep], same[keep]
    t_low = float(np.quantile(s[same], 1 - WIDE_RECALL)) if same.any() else t_high
    return t_high, round(min(t_low, t_high), 4)


# ==========================================================
# Judges
# ==========================================================

class OracleJudge:
    """Perfect operator: same case iff the case's majority issue matches."""
    name = "oracle"

    def __init__(self, issues):
        self.issues = issues

    def same(self, i, members):
        vals, counts = np.unique(self.issues[members], return_counts=True)
        return vals[counts.argmax()] == self.issues[i]

    def same_cases(self, a, b):
        major = lambda m: (lambda v, c: v[c.argmax()])(*np.unique(self.issues[m], return_counts=True))
        return major(a) == major(b)


class CEJudge:
    """Cross-encoder fine-tuned on tuning-half pairs; mean prob over rep + 2 latest members."""
    name = "ce"

    def __init__(self, texts, train_rows, issues, emb, seed):
        from sentence_transformers import CrossEncoder
        random.seed(seed)
        torch.manual_seed(seed)
        self.texts = texts
        self.model = CrossEncoder(CE_BASE, num_labels=1)
        self._fit(self._pairs(train_rows, issues, emb))

    def _pairs(self, rows, issues, emb):
        rows = np.asarray(rows)
        sims = emb[rows] @ emb[rows].T
        pos, neg = [], []
        for a in range(len(rows)):
            for b in range(a + 1, len(rows)):
                if issues[rows[a]] == issues[rows[b]]:
                    pos.append((rows[a], rows[b], 1.0))
            diff = np.where(issues[rows] != issues[rows[a]])[0]
            for b in diff[np.argsort(-sims[a][diff])[:3]]:          # hard negatives
                neg.append((rows[a], rows[b], 0.0))
            for b in random.sample(list(diff), 2):                   # easy negatives
                neg.append((rows[a], rows[b], 0.0))
        pos = random.sample(pos, min(len(pos), len(neg)))
        return pos + neg

    def _fit(self, pairs, epochs=2, batch=16, lr=3e-5):
        model, tok = self.model.model, self.model.tokenizer
        model.train()
        opt = torch.optim.AdamW(model.parameters(), lr=lr)
        loss_fn = torch.nn.BCEWithLogitsLoss()
        for _ in range(epochs):
            random.shuffle(pairs)
            for k in range(0, len(pairs), batch):
                chunk = pairs[k:k + batch]
                enc = tok([self.texts[a] for a, _, _ in chunk], [self.texts[b] for _, b, _ in chunk],
                          padding=True, truncation=True, max_length=128, return_tensors="pt").to(model.device)
                logits = model(**enc).logits.view(-1)
                loss = loss_fn(logits, torch.tensor([y for _, _, y in chunk], device=model.device))
                opt.zero_grad()
                loss.backward()
                opt.step()
        model.eval()
        self.n_pairs = len(pairs)

    def same(self, i, members):
        refs = [members[0]] + members[1:][-2:]
        probs = self.model.predict([(self.texts[i], self.texts[m]) for m in refs],
                                   activation_fn=torch.nn.Sigmoid(), show_progress_bar=False)
        return float(np.mean(probs)) >= 0.5


class TrainedJudge:
    """Pre-trained cross-encoder (Colab, rule results/training_rule.md) instead of the LLM:
    scores the new complaint against each candidate case's FIRST complaint (founder, as R1 sees),
    merges into the highest-probability case if >= 0.5, else new case."""

    def __init__(self, texts, variant):
        from sentence_transformers import CrossEncoder
        self.name = "ce" + variant
        self.texts = texts
        self.model = CrossEncoder(os.path.join(TRAINED_DIR, "ce_" + variant), num_labels=1)

    def best(self, i, candidates):
        probs = self.model.predict([(self.texts[i], self.texts[c[0]]) for c in candidates],
                                   activation_fn=torch.nn.Sigmoid(), show_progress_bar=False)
        k = int(np.argmax(probs))
        return k if probs[k] >= 0.5 else -1


class LLMJudge:
    """Groq judge. One call per banded complaint, all candidates in one prompt. Cached."""
    name = "llm"

    PROMPT = """You decide whether a new customer complaint reports the SAME underlying problem as an
existing case. Same problem = same feature and same symptom; different wording does not matter.
A different feature or a different symptom is a different problem.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"case": <case number that is the same problem, or 0 if none>}}"""

    # v2 fix for real reviews: vague complaints and "same area" must not merge.
    PROMPT_STRICT = """You decide whether a new customer complaint reports the SAME specific problem as an
existing case. Same problem = same feature AND same concrete symptom, so that one fix would solve both.
Different wording does not matter.
Answer 0 (none) when:
- the new complaint does not name a concrete symptom (e.g. only "can't login", "doesn't work", "bad app");
- it is only in the same general area (e.g. both about login, or both about tickets) but the symptom differs;
- you are not sure.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"case": <case number that is the same problem, or 0 if none>}}"""

    # v3: same strict rule, plus an explicit vague-review gate in the same call.
    PROMPT_GATED = """You decide whether a new customer complaint reports the SAME specific problem as an
existing case. Same problem = same feature AND same concrete symptom, so that one fix would solve both.
Different wording does not matter. Same general area (e.g. both about login) is NOT enough.

First decide if the new complaint is SPECIFIC: it names a concrete symptom, error or behaviour
(e.g. "access token revoked", "macros won't apply", "crashes when opening settings").
It is NOT specific if it only says something like "can't login", "doesn't work", "bad app", "too slow".

If it is not specific, or no case is the same specific problem, or you are not sure, answer case 0.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"specific": true or false, "case": <case number that is the same problem, or 0 if none>}}"""

    # User-level problem definition (results/user_level_rule.md)
    PROMPT_USER = """You decide whether a new customer complaint reports the SAME problem as an existing case,
as the USER experiences it: the same thing they cannot do, or the same visible failure
(e.g. "cannot log in", "logged out repeatedly", "notifications don't arrive", "app crashes",
"app very slow", "cannot filter tickets", "wants dark mode").
Users are not developers: different causes, error messages or details of the same experience are the
SAME problem ("invalid password", "Google sign-in loops" and just "can't log in" are all "cannot log in").
Different experiences are DIFFERENT problems ("cannot log in" vs "keeps logging me out";
"notifications don't arrive" vs "too many notifications").

First decide if the new complaint names a problem at all. It names NO problem only if it is praise,
a question, or a general rant with no problem in it ("useless app", "worst ever", a rating with no reason).

If it names no problem, or no case is the same problem, or you are not sure, answer case 0.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"problem_named": true or false, "case": <case number that is the same problem, or 0 if none>}}"""

    # Decoupled gate (results/decoupled_gate_rule.md): matching without the specificity step ...
    PROMPT_MATCH = PROMPT_GATED.replace(
        'First decide if the new complaint is SPECIFIC: it names a concrete symptom, error or behaviour\n'
        '(e.g. "access token revoked", "macros won\'t apply", "crashes when opening settings").\n'
        'It is NOT specific if it only says something like "can\'t login", "doesn\'t work", "bad app", "too slow".\n\n'
        'If it is not specific, or no case is the same specific problem, or you are not sure, answer case 0.',
        'If no case is the same specific problem, or you are not sure, answer case 0.').replace(
        'Return JSON: {{"specific": true or false, "case":', 'Return JSON: {{"case":')
    # ... and the specificity question on its own, asked once per complaint with no candidates shown
    SPECIFIC = """Decide whether this customer complaint is SPECIFIC: it names a concrete symptom, error or behaviour
(e.g. "access token revoked", "macros won't apply", "crashes when opening settings").
It is NOT specific if it only says something like "can't login", "doesn't work", "bad app", "too slow".

Complaint:
{new}

Return JSON: {{"specific": true or false}}"""

    def is_specific(self, i):
        if not hasattr(self, "spec_cache"):
            self.spec_cache, self.spec_calls = {}, 0
            self.spec_path = LLM_CACHE.replace(".jsonl", "_specific.jsonl")
            if os.path.exists(self.spec_path):
                for line in open(self.spec_path, encoding="utf-8"):
                    r = json.loads(line)
                    self.spec_cache[r["text"]] = r["specific"]
        t = self.texts[i]
        if t not in self.spec_cache:
            reply = self._call(self.SPECIFIC.format(new=t))
            self.spec_cache[t] = bool(reply.get("specific", True))
            self.spec_calls += 1
            with open(self.spec_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"text": t, "specific": self.spec_cache[t]}) + "\n")
        return self.spec_cache[t]

    # Gate wording aligned with the team codebook (results/gate_wording_rule.md)
    PROMPT_GATED_CB1 = PROMPT_GATED.replace('First decide if the new complaint is SPECIFIC: it names a concrete symptom, error or behaviour\n(e.g. "access token revoked", "macros won\'t apply", "crashes when opening settings").\nIt is NOT specific if it only says something like "can\'t login", "doesn\'t work", "bad app", "too slow".\n', 'First decide if the new complaint is SPECIFIC: it says WHAT goes wrong - a feature or action and what\nhappens to it (e.g. "access token revoked", "notifications don\'t arrive", "tickets load very slowly",\n"crashes when opening settings", "keeps logging me out", "can\'t attach files").\nIt is NOT specific only if it names no symptom at all: "bad app", "doesn\'t work", "useless",\n"worst support", praise, or a rating without a problem.\n')
    PROMPT_GATED_CB2 = PROMPT_GATED.replace('First decide if the new complaint is SPECIFIC: it names a concrete symptom, error or behaviour\n(e.g. "access token revoked", "macros won\'t apply", "crashes when opening settings").\nIt is NOT specific if it only says something like "can\'t login", "doesn\'t work", "bad app", "too slow".\n', 'First decide if the new complaint is SPECIFIC: it says WHAT goes wrong - a feature or action and what\nhappens to it (e.g. "access token revoked", "notifications don\'t arrive", "tickets load very slowly",\n"crashes when opening settings", "keeps logging me out", "can\'t attach files").\nIt is NOT specific only if it names no symptom at all: "bad app", "doesn\'t work", "useless",\n"worst support", praise, or a rating without a problem.\nA short complaint can still be specific: "too slow", "keeps logging me out", "no notifications" ARE\nspecific. A complaint is not specific only when it gives no detail of the failure, e.g. "can\'t login"\nwith nothing else, "keeps crashing" with no trigger, "app not working".\n')

    PROMPT_GATED_CB3 = PROMPT_GATED_CB2.replace('existing case. Same problem = same feature AND same concrete symptom, so that one fix would solve both.\nDifferent wording does not matter. Same general area (e.g. both about login) is NOT enough.\n', 'existing case. Same problem = the same failure of the same feature, at the level a support team would\nfile ONE ticket for (e.g. "notifications don\'t arrive" = "not getting alerts for new tickets"; but\n"login code never arrives" is NOT "password rejected"). Different details or wording do not make it a\ndifferent problem. If the new complaint mentions several problems, match on its MAIN problem.\nSame general area (e.g. both about login) is NOT enough.\n')

    PROMPT_GATED_CB4 = PROMPT_GATED_CB2.replace('Different wording does not matter. Same general area (e.g. both about login) is NOT enough.\n', 'Different wording does not matter. If the new complaint mentions several problems, match on its MAIN problem.\nSame general area (e.g. both about login) is NOT enough.\n')

    # Run 2: corrected vague rule (a slow or partly described problem is NOT vague).
    PROMPT_GATED2 = """You decide whether a new customer complaint reports the SAME specific problem as an
existing case. Same problem = same feature AND same concrete symptom, so that one fix would solve both.
Different wording does not matter. Same general area (e.g. both about login) is NOT enough.

First decide if the new complaint is VAGUE: it contains no identifiable symptom or problem.
VAGUE examples: "The app doesn't work." / "Bad app." / "Terrible experience."
NOT vague: "The app is too slow." / "Tickets take too long to load." / "I cannot see unsolved tickets."

If it is vague, or no case is the same specific problem, or you are not sure, answer case 0.

New complaint:
{new}

Existing cases (each described by its problem statement):
{cases}

Return JSON: {{"vague": true or false, "case": <case number that is the same problem, or 0 if none>}}"""

    # E1: no hard vague gate; three outcomes. UNCERTAIN goes to the human review queue.
    PROMPT_UNCERTAIN = """You decide whether a new customer complaint reports the SAME specific problem as an
existing case. Same problem = same feature AND same concrete symptom, so that one fix would solve both.
Different wording does not matter. Same general area (e.g. both about login) is NOT enough.

Choose one decision:
- "merge": there is sufficient evidence that the new complaint is the same specific problem as one case.
- "none": it is a different problem from every case.
- "uncertain": the information is genuinely insufficient to decide (e.g. the complaint is too vague,
  or it could match a case but the evidence is weak). Do not guess.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"decision": "merge" or "none" or "uncertain", "case": <case number if merge, else 0>}}"""

    # One problem statement per case, written once (symptom only, nothing invented).
    PROMPT_STATEMENT = """Extract the single concrete problem represented by this customer complaint about a
helpdesk app. Write ONE line of at most 15 words in the form "<feature>: <symptom>".
Preserve the actual symptom. Do not infer causes, intent, severity or missing details.
If several problems are present, describe the problem most clearly supported by the complaint.
If no concrete problem is stated, write "<general>: no specific problem stated".

Complaint:
{text}

Return JSON: {{"statement": "<feature>: <symptom>"}}"""

    def __init__(self, texts, refs, data="synthetic", view="founder_latest", prompt="v1"):
        from normalize import experiment_groq_clients
        self.clients = experiment_groq_clients()   # rotate to the next key when one hits its daily cap
        self.key_index = 0
        self.client = self.clients[0]
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.texts, self.refs = texts, refs
        self.cache = {}
        self.cache_path = LLM_CACHE if data.startswith("synthetic") else LLM_CACHE.replace(".jsonl", f"_{data}.jsonl")
        self.view = view
        self.prompt = {"strict": self.PROMPT_STRICT, "gated": self.PROMPT_GATED,
                       "gated2": self.PROMPT_GATED2, "uncertain": self.PROMPT_UNCERTAIN,
                       "gated_cb1": self.PROMPT_GATED_CB1, "gated_cb2": self.PROMPT_GATED_CB2,
                       "gated_cb3": self.PROMPT_GATED_CB3, "gated_cb4": self.PROMPT_GATED_CB4,
                       "match": self.PROMPT_MATCH, "user": self.PROMPT_USER}.get(prompt, self.PROMPT)
        self.three_way = prompt == "uncertain"
        if prompt == "gated_fewshot":             # R1 prompt + worked examples from the tuning side
            ex = json.load(open(FEWSHOT_PATH, encoding="utf-8"))
            lines = [f'{n + 1}. A: "{e["a"]}"\n   B: "{e["b"]}"\n   -> ' +
                     ("SAME specific problem" if e["same"] else "DIFFERENT problem") for n, e in enumerate(ex)]
            block = ("Examples of earlier decisions for this kind of product (labelled by people):\n" +
                     "\n".join(lines) + "\n\n").replace("{", "{{").replace("}", "}}")
            self.prompt = self.PROMPT_GATED.replace("New complaint:\n", block + "New complaint:\n")
            self.gated = True
        self.uncertain = set()                    # rows sent to the human review queue
        self.resolver = None                      # optional stand-in for the human (OracleJudge)
        self.show_vague = False                   # E2: keep vague-started cases visible
        self.gated = prompt in ("gated", "gated2", "gated_cb1", "gated_cb2", "gated_cb3", "gated_cb4", "user")
        self.statements = {}                      # case statements, cached separately (one per founder)
        self.statement_path = self.cache_path.replace(".jsonl", "_statements.jsonl")
        if view == "statement" and os.path.exists(self.statement_path):
            for line in open(self.statement_path, encoding="utf-8"):
                r = json.loads(line)
                self.statements[r["ref"]] = r["statement"]
        self.vague = set()                        # rows the judge called not specific
        variant = ("" if view == "founder_latest" else f"_{view}") + ("" if prompt == "v1" else f"_{prompt}")
        if variant:                               # separate cache per judge variant
            self.cache_path = self.cache_path.replace(".jsonl", f"{variant}.jsonl")
        if os.path.exists(self.cache_path):
            for line in open(self.cache_path, encoding="utf-8"):
                r = json.loads(line)
                self.cache[r["key"]] = r["answer"]
        self.calls = 0

    def _call(self, prompt):
        """One JSON call with key rotation and rate-limit waiting."""
        waited = 0
        while True:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model, temperature=0, response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": prompt}])
                return json.loads(resp.choices[0].message.content)
            except Exception as exc:
                wait = self._next_key(exc)
                if waited + wait > 26 * 3600:
                    raise RuntimeError("LLM failed repeatedly") from exc
                if wait > 0:
                    print(f"llm retry in {wait:.0f}s: {str(exc)[:100]}", flush=True)
                    time.sleep(wait)
                    waited += wait

    def _next_key(self, exc):
        """Rate-limit handling across keys. Remember when each key is free again; switch to
        the key that frees up soonest (cycling back to earlier keys). Returns seconds to wait."""
        m = re.search(r"try again in (?:(\d+)h)?(?:(\d+)m)?([\d.]+)s", str(exc))
        wait = (int(m.group(1) or 0) * 3600 + int(m.group(2) or 0) * 60 + float(m.group(3)) + 5) if m else 30
        now = time.time()
        if not hasattr(self, "free_at"):
            self.free_at = [0.0] * len(self.clients)
        self.free_at[self.key_index] = now + wait
        best = min(range(len(self.clients)), key=lambda k: self.free_at[k])
        if best != self.key_index:
            print(f"llm: key {self.key_index + 1} limited, switching to key {best + 1}", flush=True)
            self.key_index, self.client = best, self.clients[best]
        return max(0.0, self.free_at[best] - now)

    # Vague second look (results/vague_second_look_rule.md): only for complaints the gate called vague
    SECOND_LOOK = """This customer complaint is short or general. Decide whether it most likely reports the SAME
problem as one of the existing cases: the same feature AND the same kind of failure, so that fixing
that case would very likely fix this complaint too. Sharing only the general area (e.g. both about
login, or both "not working") is NOT enough. If you are not sure, answer case 0.
Also name the product area the complaint is about in 1-3 words (e.g. "login", "notifications",
"crash on launch", "sync"), or "none" if it names no area.

New complaint:
{new}

Existing cases:
{cases}

Return JSON: {{"case": <case number that is the same problem, or 0 if none>, "area": "<area or none>"}}"""

    def second_look(self, i, candidates):
        """Case index (0-based) the vague complaint i most likely belongs to, or -1; area stored."""
        if not hasattr(self, "sl_cache"):
            self.sl_cache, self.sl_calls = {}, 0
            self.sl_path = self.cache_path.replace(".jsonl", "_secondlook.jsonl")
            if os.path.exists(self.sl_path):
                for line in open(self.sl_path, encoding="utf-8"):
                    r = json.loads(line)
                    self.sl_cache[r["key"]] = r["reply"]
        shown = [[c[0]] for c in candidates]                 # founder text, as R1's judge sees it
        key = json.dumps([int(self.refs[i]), [[int(self.refs[m]) for m in sh] for sh in shown]])
        if key not in self.sl_cache:
            cases = "\n".join(f"Case {n + 1}: " + self.texts[sh[0]] for n, sh in enumerate(shown))
            reply = self._call(self.SECOND_LOOK.format(new=self.texts[i], cases=cases))
            try:
                ans = int(reply.get("case", 0) or 0)
            except (TypeError, ValueError):
                ans = 0
            self.sl_cache[key] = {"case": ans, "area": str(reply.get("area", "none"))}
            self.sl_calls += 1
            with open(self.sl_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "reply": self.sl_cache[key]}) + "\n")
        ans = self.sl_cache[key]["case"]
        return ans - 1 if 1 <= ans <= len(candidates) else -1

    def statement(self, row):
        """Problem statement of a case, generated once from its first complaint."""
        ref = int(self.refs[row])
        if ref not in self.statements:
            reply = self._call(self.PROMPT_STATEMENT.format(text=self.texts[row]))
            s = str(reply.get("statement", "")).strip()
            self.statements[ref] = s or self.texts[row][:120]
            self.calls += 1
            with open(self.statement_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"ref": ref, "statement": self.statements[ref]}) + "\n")
        return self.statements[ref]

    def same_cases(self, a, b):
        """Case-merge check: the two cases' first complaints, strict rule. Cached."""
        if not hasattr(self, "merge_cache"):
            self.merge_path = self.cache_path.replace(".jsonl", "_merge.jsonl")
            self.merge_cache = {}
            if os.path.exists(self.merge_path):
                for line in open(self.merge_path, encoding="utf-8"):
                    r = json.loads(line)
                    self.merge_cache[r["key"]] = r["same"]
        x, y = sorted((int(self.refs[a[0]]), int(self.refs[b[0]])))
        key = json.dumps([x, y])
        if key not in self.merge_cache:
            ra, rb = (a[0], b[0]) if int(self.refs[a[0]]) == x else (b[0], a[0])
            reply = self._call(MERGE_PROMPT.format(a=self.texts[ra], b=self.texts[rb]))
            self.merge_cache[key] = bool(reply.get("same", False))
            self.calls += 1
            with open(self.merge_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "same": self.merge_cache[key]}) + "\n")
        return self.merge_cache[key]

    def choose(self, i, candidates, shown=None):
        """candidates: list of member-row lists (shown: rows to display per case,
        overrides the view). Returns index of chosen case or -1."""
        if shown is not None:
            pass
        elif self.view in ("founder", "statement"):  # first complaint only (or its problem statement)
            if self.show_vague:                   # E2: first complaint that was not gated vague
                shown = [[next((m for m in c if m not in self.vague), c[0])] for c in candidates]
            else:
                shown = [[c[0]] for c in candidates]
        else:
            shown = [[m for m in ([c[0]] + c[1:][-1:])] for c in candidates]
        key = json.dumps([int(self.refs[i]), [[int(self.refs[m]) for m in s] for s in shown]])
        if key not in self.cache:
            if self.view == "statement":
                cases = "\n".join(f"Case {n + 1}: " + self.statement(s[0]) for n, s in enumerate(shown))
            else:
                cases = "\n".join(f"Case {n + 1}: " + " | ".join(self.texts[m] for m in s)
                                  for n, s in enumerate(shown))
            prompt = self.prompt.format(new=self.texts[i], cases=cases)
            waited = 0
            for attempt in range(10_000):     # rate limits: wait as long as Groq says (daily cap: up to 26 h)
                try:
                    resp = self.client.chat.completions.create(
                        model=self.model, temperature=0, response_format={"type": "json_object"},
                        messages=[{"role": "user", "content": prompt}])
                    reply = json.loads(resp.choices[0].message.content)
                    answer = int(reply.get("case", 0) or 0)
                    if self.three_way:
                        decision = str(reply.get("decision", "none")).lower()
                        answer = answer if decision == "merge" else (-2 if decision == "uncertain" else 0)
                    if self.gated and (not bool(reply.get("specific", True)) or bool(reply.get("vague", False))
                                       or not bool(reply.get("problem_named", True))):
                        answer = -1               # vague: new case, never offered as a candidate
                    break
                except Exception as exc:
                    wait = self._next_key(exc)
                    if waited + wait > 26 * 3600:
                        break
                    if wait > 0:
                        print(f"llm retry in {wait:.0f}s: {str(exc)[:100]}", flush=True)
                    time.sleep(wait)
                    waited += wait
            else:
                raise RuntimeError("LLM judge failed repeatedly")
            self.calls += 1
            self.cache[key] = answer
            with open(self.cache_path, "a", encoding="utf-8") as f:
                f.write(json.dumps({"key": key, "answer": answer}) + "\n")
        answer = self.cache[key]
        if answer == -1:
            self.vague.add(i)
        if answer == -2:
            self.uncertain.add(i)
            if self.resolver is not None:          # human review queue resolves it
                for n, c in enumerate(candidates):
                    if self.resolver.same(i, c):
                        return n
            return -1
        return answer - 1 if 1 <= answer <= len(candidates) else -1


# ==========================================================
# Three-way online assignment
# ==========================================================

MAX_EXEMPLARS = 5     # E8: up to 5 diverse member complaints per case
DIVERSE_SIM = 0.85    # a member becomes an exemplar only if it is not a near-copy of one already kept


def three_way(emb, rows, t_high, t_low, judge, exemplars=False):
    """Online three-way assignment. exemplars=False: a case is its first complaint.
    exemplars=True: a case is scored by its best-matching exemplar (E8), and the
    LLM judge sees the first complaint plus that matched exemplar."""
    reps, members, ex = [], [], []
    labels = np.empty(len(rows), dtype=int)
    banded = judged_pairs = 0
    for k, i in enumerate(rows):
        if reps:
            if exemplars:
                vg = getattr(judge, "vague", set()) if getattr(judge, "show_vague", False) else set()
                per_case = [emb[[m for m in e if m not in vg] or e] @ emb[i] for e in ex]
                sims = np.array([float(s.max()) for s in per_case])
                matched = [([m for m in e if m not in vg] or e)[int(np.argmax(s))] for e, s in zip(ex, per_case)]
            else:
                sims = np.array(reps) @ emb[i]
            order = np.argsort(-sims)
            best = sims[order[0]]
            if best >= t_high:
                labels[k] = order[0]
                members[order[0]].append(i)
                if exemplars:
                    _add_exemplar(ex[order[0]], i, emb)
                continue
            if best >= t_low:
                banded += 1
                vague = getattr(judge, "vague", set())
                if getattr(judge, "show_vague", False):
                    vague = set()
                cands = [c for c in order if sims[c] >= t_low and members[c][0] not in vague][:MAX_CANDIDATES]
                chosen = -1
                if isinstance(judge, LLMJudge):
                    judged_pairs += 1
                    shown = None
                    if exemplars and judge.view in ("ex3", "ex5"):     # first complaint + stored diverse exemplars
                        k = 3 if judge.view == "ex3" else 5
                        shown = [ex[c][:k] for c in cands]
                    elif exemplars and judge.view not in ("founder", "statement"):
                        shown = [[members[c][0]] + ([matched[c]] if matched[c] != members[c][0] else [])
                                 for c in cands]
                    if PRE_GATE and not judge.is_specific(i):
                        judge.vague.add(i)                # decoupled gate: vague singleton, never a candidate
                        pick = -1
                    else:
                        pick = judge.choose(i, [members[c] for c in cands], shown)
                    chosen = cands[pick] if pick >= 0 else -1
                    if REQUIRE_TOP1 and chosen >= 0 and chosen != cands[0]:
                        chosen = -1               # LLM and cosine disagree on the best case: no merge
                    if SECOND_LOOK and chosen < 0 and i in judge.vague and cands:
                        sl = judge.second_look(i, [members[c] for c in cands])
                        if sl >= 0 and (SECOND_LOOK != "top1" or sl == 0):
                            labels[k] = cands[sl]                 # member only: not founder, not exemplar,
                            members[cands[sl]].append(i)          # so no later decision changes
                            judge.recovered = getattr(judge, "recovered", 0) + 1
                            continue
                elif isinstance(judge, TrainedJudge):
                    judged_pairs += len(cands)
                    pick = judge.best(i, [members[c] for c in cands])
                    chosen = cands[pick] if pick >= 0 else -1
                else:
                    for c in cands:
                        judged_pairs += 1
                        if judge.same(i, members[c]):
                            chosen = c
                            break
                if chosen >= 0:
                    labels[k] = chosen
                    members[chosen].append(i)
                    if exemplars:
                        _add_exemplar(ex[chosen], i, emb)
                    continue
        reps.append(emb[i])
        members.append([i])
        ex.append([i])
        labels[k] = len(reps) - 1
    return labels, banded, judged_pairs


def _add_exemplar(case_ex, i, emb):
    if len(case_ex) < MAX_EXEMPLARS and float(np.max(emb[case_ex] @ emb[i])) < DIVERSE_SIM:
        case_ex.append(i)


MERGE_PROMPT = """Two existing cases each started from a customer complaint about a helpdesk app.
Do they report the SAME specific problem? Same problem = same feature AND same concrete symptom,
so that one fix would solve both. Different wording does not matter. Same general area
(e.g. both about login) is NOT enough. If either complaint has no identifiable symptom, or you
are not sure, answer false.

Case A:
{a}

Case B:
{b}

Return JSON: {{"same": true or false}}"""


def consolidate(emb, rows, labels, groups, t_low, judge, texts=None, refs=None):
    """Periodic case-merge pass (run once after online assignment, per product).
    For each case, its nearest other case (best member-to-member cosine) is a
    merge candidate if that similarity is >= t_low. Candidate pairs are checked in
    order of similarity; the judge sees the two cases' first complaints.
    Returns new labels aligned with rows."""
    labels = np.asarray(labels).copy()
    parent = {int(c): int(c) for c in np.unique(labels)}

    def find(c):
        while parent[c] != c:
            parent[c] = parent[parent[c]]
            c = parent[c]
        return c

    checked = 0
    for g in pd.unique(groups[rows]):
        pos = np.where(groups[rows] == g)[0]
        cases = {}
        for p in pos:                                   # rows are in arrival order
            cases.setdefault(int(labels[p]), []).append(int(rows[p]))
        vague = getattr(judge, "vague", set())
        ids = [c for c, m in cases.items() if m[0] not in vague]
        pairs = {}
        for c in ids:
            best, best_s = None, -1.0
            for o in ids:
                if o == c:
                    continue
                s = float(np.max(emb[cases[c]] @ emb[cases[o]].T))
                if s > best_s:
                    best, best_s = o, s
            if best is not None and best_s >= t_low:
                pairs[tuple(sorted((c, best)))] = best_s
        for (c, o), s in sorted(pairs.items(), key=lambda kv: -kv[1]):
            if find(c) == find(o):
                continue
            checked += 1
            if judge.same_cases(cases[c], cases[o]):
                parent[find(o)] = find(c)
    merged = np.array([find(int(c)) for c in labels])
    return merged, checked


def by_group(cluster, rows, groups):
    """Apply cluster(rows) inside each group; return labels aligned with rows."""
    labels = np.empty(len(rows), dtype=np.int64)
    extra = [0, 0]
    offset = 0
    g_rows = groups[rows]
    for g in pd.unique(g_rows):
        pos = np.where(g_rows == g)[0]
        lab, banded, pairs = cluster(rows[pos])
        _, lab = np.unique(lab, return_inverse=True)
        labels[pos] = lab + offset
        offset += lab.max() + 1
        extra[0] += banded
        extra[1] += pairs
    return labels, extra[0], extra[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--judges", nargs="+", default=["single", "oracle", "ce"])
    parser.add_argument("--seeds", nargs="+", type=int, default=SPLIT_SEEDS)
    parser.add_argument("--data", default="synthetic", choices=list(DATA_PATHS))
    parser.add_argument("--top-k", type=int, default=MAX_CANDIDATES,
                        help="candidate cases shown to the judge (default 3)")
    parser.add_argument("--retrieval", default="founder", choices=["founder", "exemplars"],
                        help="exemplars: score cases by up to 5 diverse member complaints (E8)")
    parser.add_argument("--judge-view", default="founder_latest", choices=["founder_latest", "founder", "statement", "ex3", "ex5"],
                        help="what the LLM sees of each candidate case")
    parser.add_argument("--judge-prompt", default="v1",
                        choices=["v1", "strict", "gated", "gated2", "uncertain", "gated_fewshot",
                                 "gated_cb1", "gated_cb2", "gated_cb3", "gated_cb4", "match", "user"])
    parser.add_argument("--require-top1", action="store_true",
                        help="automatic merge only when the LLM's chosen case is also the top cosine candidate")
    parser.add_argument("--fewshot", default="", help="examples JSON for --judge-prompt gated_fewshot")
    parser.add_argument("--show-vague-cases", action="store_true",
                        help="E2: cases started by a vague complaint stay visible (matched on informative members)")
    parser.add_argument("--consolidate", action="store_true",
                        help="also report a periodic case-merge pass after online assignment")
    parser.add_argument("--halves", default="BA", help="which held-out halves to run, e.g. B (development)")
    parser.add_argument("--band", default="narrow", choices=["narrow", "wide"],
                        help="wide: t_low keeps 80%% of tuning duplicate pairs (real data)")
    parser.add_argument("--per-product", action="store_true",
                        help="cluster each product separately (one company's complaints at a time)")
    parser.add_argument("--calibrate-on", default="",
                        help="external test: fit band/threshold ONLY on this dataset, test on all of --data")
    parser.add_argument("--lopo", action="store_true",
                        help="leave-one-product-out: calibrate on the other products, test on each product in turn")
    parser.add_argument("--embed", default="", help="retrieval encoder path (default MiniLM), e.g. the trained bi_C")
    parser.add_argument("--pre-gate", action="store_true",
                        help="decoupled gate: specificity asked alone first (results/decoupled_gate_rule.md)")
    parser.add_argument("--second-look", default="", choices=["", "any", "top1"],
                        help="vague second look (results/vague_second_look_rule.md): any = VS, top1 = VS1")
    args = parser.parse_args()
    globals()["MAX_CANDIDATES"] = args.top_k
    globals()["FEWSHOT_PATH"] = args.fewshot
    globals()["REQUIRE_TOP1"] = args.require_top1
    globals()["SECOND_LOOK"] = args.second_look
    globals()["PRE_GATE"] = args.pre_gate

    from sentence_transformers import SentenceTransformer
    encoder = SentenceTransformer(args.embed or EMBED_MODEL)
    if args.calibrate_on:                         # calibration rows first, then the test dataset
        cal = load_ground_truth(path=DATA_PATHS[args.calibrate_on])
        tgt = load_ground_truth(path=DATA_PATHS[args.data])
        tgt["complaint_ref"] = tgt["complaint_ref"] + EXT_REF_OFFSET     # keep refs unique across datasets
        cols = ["complaint_ref", "department", "issue_id", "complaint_text"]
        raw = pd.concat([cal[cols].assign(_cal=True), tgt[cols].assign(_cal=False)], ignore_index=True)
    else:
        raw = load_ground_truth(path=DATA_PATHS[args.data])
    df = apply_text_mode(raw, "boilerplate", encoder)
    judge_text = boilerplate_suppress(df["complaint_text"].astype(str).tolist(), encoder)
    emb = encoder.encode(df["cleaned_text"].tolist(), normalize_embeddings=True, show_progress_bar=False)
    issues = np.array(df["issue_id"].astype(str).tolist())
    refs = df["complaint_ref"].values
    issue_ids = np.array(sorted(set(issues)))
    cache_name = f"{args.data}_ext_{args.calibrate_on}" if args.calibrate_on else args.data
    if args.data == "playstore_user":             # same refs as playstore for the 338 shared reviews: reuse R1's answers
        cache_name = "playstore"
    llm = LLMJudge(judge_text, refs, cache_name, args.judge_view, args.judge_prompt) if "llm" in args.judges else None
    if llm is not None:
        llm.show_vague = args.show_vague_cases
        if args.judge_prompt == "uncertain":      # also report: uncertain queue resolved by a human
            args.judges = list(args.judges) + ["llm_human"]

    out, assignments = [], []
    prefix = "" if args.data == "synthetic" else f"{args.data}_"
    tag = "_".join(args.judges) + ("" if args.seeds == SPLIT_SEEDS else "_seeds" + "".join(map(str, args.seeds)))
    groups = np.array(df["department"].astype(str).tolist()) if args.per_product else None
    if args.per_product:
        from compare_pipelines import per_product
        tag += "_perproduct"
    if args.band == "wide":
        tag += "_wideband"
    if args.retrieval == "exemplars":
        tag += "_exemplars"
    if args.top_k != 3:
        tag += f"_top{args.top_k}"
    if args.halves != "BA":
        tag += f"_half{args.halves}"
    if args.consolidate:
        tag += "_merge"
    if args.show_vague_cases:
        tag += "_showvague"
    if args.require_top1:
        tag += "_top1agree"
    if "llm" in args.judges and (args.judge_view != "founder_latest" or args.judge_prompt != "v1"):
        tag += f"_{args.judge_view}_{args.judge_prompt}"
    if args.pre_gate:
        tag += "_pregate"
    if args.second_look:
        tag += "_secondlook" + ("" if args.second_look == "any" else "_top1")
    if args.embed:
        tag += "_emb" + os.path.basename(os.path.normpath(args.embed))
    if args.calibrate_on:
        tag += f"_ext_{args.calibrate_on}"
        is_cal = df["_cal"].to_numpy(dtype=bool)
        splits = [("ext", args.data, np.where(is_cal)[0], np.where(~is_cal)[0])]
    elif args.lopo:
        tag += "_lopo"
        products = np.array(df["department"].astype(str).tolist())
        splits = [("lopo", p, np.where(products != p)[0], np.where(products == p)[0])
                  for p in pd.unique(products)]
    else:
        splits = []
        for seed in args.seeds:
            rng = np.random.default_rng(seed)
            half = set(rng.choice(issue_ids, size=len(issue_ids) // 2, replace=False))
            a = np.where(np.isin(issues, list(half)))[0]
            b = np.where(~np.isin(issues, list(half)))[0]
            splits += [(seed, h, tn, ts) for h, (tn, ts) in (("B", (a, b)), ("A", (b, a))) if h in args.halves]
    for seed, h, tune, test in splits:
        if True:
            bands = band_thresholds_wide if args.band == "wide" else band_thresholds
            t_high, t_low = bands(emb[tune], issues[tune], None if groups is None else groups[tune])
            for name in args.judges:
                t0 = time.time()
                if name == "single":
                    run = lambda d, e, t: online_cos(e, t)
                    if groups is not None:
                        run = per_product(run)
                    t = pick_threshold(run, df, emb, tune, np.round(np.arange(0.30, 0.96, 0.02), 3))
                    labels, banded, pairs = run(df.iloc[test].reset_index(drop=True), emb[test], t), 0, 0
                    info = f"t*={t:.2f}"
                else:
                    judge = {"oracle": lambda: OracleJudge(issues),
                             "ce": lambda: CEJudge(judge_text, tune, issues, emb, seed),
                             "ceA": lambda: TrainedJudge(judge_text, "A"), "ceB": lambda: TrainedJudge(judge_text, "B"),
                             "llm": lambda: llm, "llm_human": lambda: llm}[name]()
                    if llm is not None:
                        llm.resolver = OracleJudge(issues) if name == "llm_human" else None
                        llm.uncertain.clear()
                    if groups is None:
                        labels, banded, pairs = three_way(emb, test, t_high, t_low, judge, args.retrieval == "exemplars")
                    else:
                        labels, banded, pairs = by_group(
                            lambda r: three_way(emb, r, t_high, t_low, judge, args.retrieval == "exemplars"), test, groups)
                    info = f"band=[{t_low:.2f},{t_high:.2f})"
                m = evaluate(labels, issues[test], np.arange(len(test)))
                assignments += [{"judge": name, "split_seed": seed, "held_out_half": h,
                                 "complaint_ref": int(refs[r]), "case": int(c)} for r, c in zip(test, labels)]
                if llm is not None and name in ("llm", "llm_human"):
                    m["review_queue"] = len(set(test.tolist()) & llm.uncertain)
                    m["vague_gated"] = len(set(test.tolist()) & llm.vague)
                    m["vague_recovered"] = getattr(llm, "recovered", 0)
                    llm.recovered = 0
                m.update({"judge": name, "split_seed": seed, "held_out_half": h,
                          "t_low": t_low, "t_high": t_high, "banded_complaints": banded,
                          "banded_share": banded / len(test), "judge_pairs": pairs,
                          "seconds": round(time.time() - t0, 1)})
                out.append(m)
                print(f"seed={seed} {h} {name:6s} {info:18s} P={m['pair_precision']:.3f} "
                      f"R={m['pair_recall']:.3f} F1={m['pair_f1']:.3f} cases={m['cases']} "
                      f"contam={m['contaminated_cases']} banded={banded}/{len(test)} "
                      f"pairs={pairs} queue={m.get('review_queue', 0)} ({m['seconds']}s)", flush=True)
                if args.consolidate and name in ("oracle", "llm") and groups is not None:
                    t1 = time.time()
                    merged, checked = consolidate(emb, test, labels, groups, t_low, judge)
                    mm = evaluate(merged, issues[test], np.arange(len(test)))
                    assignments += [{"judge": f"{name}+merge", "split_seed": seed, "held_out_half": h,
                                     "complaint_ref": int(refs[r]), "case": int(c)} for r, c in zip(test, merged)]
                    mm.update({"judge": f"{name}+merge", "split_seed": seed, "held_out_half": h,
                               "t_low": t_low, "t_high": t_high, "banded_complaints": banded,
                               "banded_share": banded / len(test), "judge_pairs": pairs + checked,
                               "seconds": round(time.time() - t1, 1)})
                    out.append(mm)
                    print(f"seed={seed} {h} {name + '+merge':10s} checked={checked:<4d}     "
                          f"P={mm['pair_precision']:.3f} R={mm['pair_recall']:.3f} F1={mm['pair_f1']:.3f} "
                          f"cases={mm['cases']} contam={mm['contaminated_cases']}", flush=True)
                pd.DataFrame(out).to_csv(os.path.join(RESULTS, f"{prefix}e5_three_way_{tag}.csv"), index=False)
                pd.DataFrame(assignments).to_csv(os.path.join(RESULTS, f"{prefix}e5_assignments_{tag}.csv"),
                                                 index=False)

    res = pd.DataFrame(out)
    cols = ["pair_precision", "pair_recall", "pair_f1", "cases", "contaminated_cases", "banded_share"]
    print("\n", res.groupby("judge")[cols].agg(["mean", "std"]).round(3).to_string())
    if llm:
        print("new LLM calls this run:", llm.calls)


if __name__ == "__main__":
    main()
