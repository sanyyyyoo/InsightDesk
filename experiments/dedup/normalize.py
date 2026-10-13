"""
E4: text normalisation before dedup, without and with an LLM.

  E4a  boilerplate suppression (no LLM, no labels)
       Split each complaint into segments. A segment is boilerplate when
       near-copies of it occur in many complaints whose REMAINING text is
       unrelated: filler repeats across different problems, a real symptom
       repeats within one problem. The generator's phrase list and the
       issue labels are never used.

  E4b  LLM normalisation (Groq, batched)
       Rewrite each complaint into a short issue statement. Complaints are
       sent 10 per call and cached, so a rerun makes no API calls.

  python experiments/dedup/normalize.py --llm      # build the E4b cache
"""

import argparse
import json
import os
import re
import sys
import time

import numpy as np
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

RESULTS = os.path.join(os.path.dirname(__file__), "results")
DATA_PATHS = {
    "synthetic": "data/synthetic_ground_truth.csv",
    "gitbugs_user": "data/external/gitbugs_user.csv",
    "gitbugs_template": "data/external/gitbugs_template.csv",
    # same 488 synthetic complaints, Krisha-corrected case-level labels (build_l1_labels.py)
    "synthetic_l1": "experiments/dedup/labels/synthetic_l1.csv",
    # team-labelled real Play Store reviews (build_playstore_testset.py)
    "playstore": "data/external/playstore_scored.csv",
    "playstore_all": "data/external/playstore_all.csv",
    # user-level problems (labels/playstore_user_level_map.csv, approved 2026-10-13)
    "playstore_user": "data/external/playstore_user.csv",
    # Firefox duplicate-bug benchmark, cross-domain test (build_firefox_dbrd.py)
    "firefox": "data/external/firefox.csv",
    "firefox2": "data/external/firefox2.csv",
    "firefox3": "data/external/firefox3.csv",
    "thunderbird": "data/external/thunderbird.csv",
    # new help-desk apps (new_apps_rule.md): the 588-review blind sheet, no labels at run time
    "new_apps": "data/external/new_apps_all.csv",
    # Jira Cloud alone (one company), separate blind run with its own caches
    "jira_new": "data/external/jira_new.csv",
    # same 200 Jira reviews, issue_id = agreed Claude/ChatGPT key (leak analysis only)
    "jira_agreed": "data/external/jira_agreed.csv",
}


EXPERIMENT_ENV = os.path.join(os.path.dirname(__file__), "..", "..", ".env.experiments")


def experiment_groq_clients():
    """Groq clients for offline experiments ONLY, from .env.experiments
    (git-ignored): GROQ_API_KEY_EXPERIMENTS, GROQ_API_KEY_EXPERIMENTS_2, ...
    The app's shared RCA / chatbot key is used only if EXPERIMENTS_ALLOW_APP_KEY=1,
    and then last, after every experiment key has hit its daily cap."""
    from dotenv import dotenv_values
    from groq import Groq
    env = dotenv_values(EXPERIMENT_ENV)
    names = sorted((k for k in env if k.startswith("GROQ_API_KEY_EXPERIMENTS")),
                   key=lambda k: (k != "GROQ_API_KEY_EXPERIMENTS", k))
    keys = [(env[k] or "").strip() for k in names]
    keys = [k for k in keys if k and not k.startswith("paste")]
    if os.getenv("EXPERIMENTS_ALLOW_APP_KEY") == "1":
        app = (dotenv_values("D:/PBL/InsightDesk/.env").get("GROQ_API_KEY") or "").strip()
        if app and app not in keys:
            keys.append(app)
    if not keys:
        raise SystemExit(f"Set GROQ_API_KEY_EXPERIMENTS in {os.path.abspath(EXPERIMENT_ENV)} first.")
    return [Groq(api_key=k) for k in keys]


def experiment_groq_client():
    return experiment_groq_clients()[0]


def llm_cache_path(data="synthetic"):
    # synthetic_* variants share the synthetic texts, so they share the cache
    name = "llm_normalized.csv" if data.startswith("synthetic") else f"llm_normalized_{data}.csv"
    return os.path.join(RESULTS, name)

# ==========================================================
# E4a: boilerplate suppression
# ==========================================================

# A short lead-in ending in ":" or " - " ("Update:", "Hi team -") is its own segment.
LEAD_IN = re.compile(r"^\s*((?:\S+\s+){0,5}\S+?)\s*(?::|\s-)\s+(?=\S)")
# Sentence ends, and line breaks (real reports put template fields on separate lines).
SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\s*\n+\s*")

NEAR_COPY = 0.90      # segment-to-segment cosine counted as "the same sentence"
MIN_HOSTS = 8         # a segment must recur in at least this many complaints
MAX_HOST_COHESION = 0.30  # mean cosine between the hosts' remaining text


def split_segments(text):
    text = text.strip()
    segments = []
    lead = LEAD_IN.match(text)
    if lead:
        segments.append(lead.group(1))
        text = text[lead.end():]
    segments += [s for s in SENTENCE_END.split(text) if s.strip()]
    return segments


def _unit(v):
    return v / np.clip(np.linalg.norm(v, axis=-1, keepdims=True), 1e-12, None)


def boilerplate_suppress(texts, encoder, verbose=False, return_report=False):
    """Return texts with boilerplate segments removed (keeps at least one segment)."""
    segs = [split_segments(t) for t in texts]
    flat = [(i, j, s) for i, ss in enumerate(segs) for j, s in enumerate(ss)]
    seg_emb = encoder.encode([s for _, _, s in flat], normalize_embeddings=True,
                             show_progress_bar=False)
    owner = np.array([i for i, _, _ in flat])
    sims = seg_emb @ seg_emb.T

    # Pass 1: segments that recur in many complaints are candidates.
    hosts_of = {}
    for a, (i, _, _) in enumerate(flat):
        docs = set(owner[sims[a] >= NEAR_COPY].tolist()) | {i}
        if len(docs) >= MIN_HOSTS:
            hosts_of[a] = docs
    candidate = set(hosts_of)

    # Pass 2: a candidate is boilerplate when the hosts' text WITHOUT any
    # candidate segment is unrelated. (Judging the rest with other filler
    # still in it would make any repeated symptom look like boilerplate.)
    # Each complaint's text without any candidate segment, embedded once.
    rest = [[] for _ in segs]
    for a, (i, _, s) in enumerate(flat):
        if a not in candidate:
            rest[i].append(s)
    has_rest = np.array([bool(r) for r in rest])
    rest_emb = np.zeros((len(segs), seg_emb.shape[1]), dtype=seg_emb.dtype)
    if has_rest.any():
        rest_emb[has_rest] = encoder.encode([" ".join(r) for r in rest if r],
                                            normalize_embeddings=True, show_progress_bar=False)

    boiler, report, checked = set(), [], {}
    for a, docs in hosts_of.items():
        s = flat[a][2]
        key = s.lower().strip()
        if key not in checked:
            usable = [d for d in docs if has_rest[d]]
            if len(usable) < MIN_HOSTS // 2:
                checked[key] = None               # cannot judge: keep
            else:
                e = rest_emb[usable]
                n = len(e)
                checked[key] = float(((e @ e.T).sum() - n) / (n * (n - 1)))
        cohesion = checked[key]
        drop = cohesion is not None and cohesion <= MAX_HOST_COHESION
        if drop:
            boiler.add(a)
        report.append((s, len(docs), -1.0 if cohesion is None else round(cohesion, 3), drop))

    if verbose:
        seen = set()
        for s, n, c, b in sorted(report, key=lambda r: -r[1]):
            if s.lower() in seen:
                continue
            seen.add(s.lower())
            print(f"{'DROP' if b else 'keep'} hosts={n:3d} cohesion={c:.3f}  {s[:80]}")

    kept = [[] for _ in segs]
    for a, (i, _, s) in enumerate(flat):
        if a not in boiler:
            kept[i].append(s)
    out = [" ".join(k) if k else " ".join(ss) for k, ss in zip(kept, segs)]
    if return_report:
        # (segment, complaints containing a near-copy, rest cohesion or -1, dropped?)
        return out, report
    return out


# ==========================================================
# E4b: LLM normalisation
# ==========================================================

PROMPT = """You normalise customer complaints about a B2B SaaS product before duplicate detection.
For each complaint, write ONE short issue statement (max 15 words) that names the affected feature
and the concrete symptom, plus any error message or trigger that is stated.
Leave out greetings, follow-up or repeat markers, urgency, frequency, impact on the customer,
and requests for help. Do not guess causes. Do not merge complaints.

Return JSON: {{"items": [{{"id": <id>, "issue": "<statement>"}}, ...]}} with one item per complaint.

Complaints:
{items}"""


def llm_normalize(df, batch=10, model=None, data="synthetic"):
    LLM_CACHE = llm_cache_path(data)
    client = experiment_groq_client()
    model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    cache = pd.read_csv(LLM_CACHE) if os.path.exists(LLM_CACHE) else \
        pd.DataFrame(columns=["complaint_ref", "issue_statement"])
    done = set(cache["complaint_ref"].astype(int))
    todo = df[~df["complaint_ref"].isin(done)]
    calls = 0

    for start in range(0, len(todo), batch):
        chunk = todo.iloc[start:start + batch]
        items = "\n".join(f'{r.complaint_ref}: ' + " ".join(str(r.complaint_text).split())
                          for r in chunk.itertuples())
        for attempt in range(6):
            try:
                resp = client.chat.completions.create(
                    model=model, temperature=0,
                    response_format={"type": "json_object"},
                    messages=[{"role": "user", "content": PROMPT.format(items=items)}],
                )
                calls += 1
                got = {int(x["id"]): x["issue"] for x in json.loads(resp.choices[0].message.content)["items"]}
                break
            except Exception as exc:  # rate limit or malformed JSON: back off and retry
                wait = 10 * (attempt + 1)
                print(f"retry in {wait}s: {str(exc)[:120]}", flush=True)
                time.sleep(wait)
        else:
            raise RuntimeError("LLM normalisation failed repeatedly")

        rows = [{"complaint_ref": r.complaint_ref,
                 "issue_statement": got.get(int(r.complaint_ref), r.complaint_text)}
                for r in chunk.itertuples()]
        cache = pd.concat([cache, pd.DataFrame(rows)], ignore_index=True)
        cache.to_csv(LLM_CACHE, index=False)
        print(f"{len(cache)}/{len(df)} normalised ({calls} calls)", flush=True)

    return calls


# ==========================================================
# E6a: domain term normalisation (no LLM)
# ==========================================================

# Nouns/objects only (failure words are never mapped). Built from Play Store
# review evidence and general helpdesk/auth vocabulary; see the file.
SYNONYMS_PATH = os.path.join(os.path.dirname(__file__), "labels", "domain_synonyms.csv")
_SYN = None


def apply_synonyms(text, skip_canonical=()):
    global _SYN
    if _SYN is None:
        m = pd.read_csv(SYNONYMS_PATH)
        m = m.assign(n=m.variant.str.len()).sort_values("n", ascending=False)   # longest first
        _SYN = [(re.compile(r"(?<![a-z0-9])" + re.escape(v) + r"(?![a-z0-9])", re.I), c)
                for v, c in zip(m.variant, m.canonical)]
    for pattern, canonical in _SYN:
        if canonical not in skip_canonical:
            text = pattern.sub(canonical, text)
    return text


def apply_text_mode(df, mode, encoder=None, data="synthetic"):
    """Replace df['cleaned_text'] according to the E4 text mode."""
    from backend.services.preprocess import clean_text
    from replay_lab import strip_generator_templates

    raw = df["complaint_text"].astype(str)
    if mode == "raw":
        text = raw
    elif mode == "stripped":          # upper bound: generator phrases removed by hand
        text = raw.map(strip_generator_templates)
    elif mode == "boilerplate":       # E4a
        text = pd.Series(boilerplate_suppress(raw.tolist(), encoder), index=df.index)
    elif mode == "llm":               # E4b
        cache = pd.read_csv(llm_cache_path(data)).set_index("complaint_ref")["issue_statement"]
        text = df["complaint_ref"].map(cache).fillna(raw)
    elif mode.startswith("boilerplate+synonyms"):   # E6a
        skip = {"verification code"} if mode.endswith("_nocode") else set()
        text = pd.Series(boilerplate_suppress(raw.tolist(), encoder), index=df.index)
        text = text.map(lambda t: apply_synonyms(t, skip))
    else:
        raise ValueError(mode)
    df = df.copy()
    df["cleaned_text"] = text.map(clean_text)
    return df


if __name__ == "__main__":
    sys.path.append(os.path.dirname(__file__))
    from replay_lab import load_ground_truth

    parser = argparse.ArgumentParser()
    parser.add_argument("--llm", action="store_true", help="build the E4b cache")
    parser.add_argument("--show-boilerplate", action="store_true")
    parser.add_argument("--data", default="synthetic", choices=list(DATA_PATHS))
    args = parser.parse_args()
    df = load_ground_truth(path=DATA_PATHS[args.data])

    if args.show_boilerplate:
        from sentence_transformers import SentenceTransformer
        enc = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        boilerplate_suppress(df["complaint_text"].astype(str).tolist(), enc, verbose=True)
    if args.llm:
        print("LLM calls:", llm_normalize(df, data=args.data))
