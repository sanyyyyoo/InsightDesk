"""
Label-free boilerplate suppression (Phase 1), as tested in experiments/dedup/normalize.py (E4a).

A segment (lead-in phrase, sentence or line) is a boilerplate candidate when a near-copy of it
(segment cosine >= NEAR_COPY) occurs in at least MIN_HOSTS complaints, and it is boilerplate when the
rest of those complaints is unrelated (mean pairwise cosine of their remaining text <= MAX_HOST_COHESION),
as with "Hi team, please help". Repeated symptoms ("the OTP never arrives") are kept, because the
complaints that share them are about the same thing.

Online use: refresh() runs the detection over the most recent stored complaints (scheduled every
6 hours with re-joining) and saves the boilerplate segments; strip() drops the segments of a new
complaint that are near-copies of a saved one, always keeping at least one segment. With no saved
list, strip() returns the text unchanged.
"""

import json
import os
import re

import numpy as np

LEAD_IN = re.compile(r"^\s*((?:\S+\s+){0,5}\S+?)\s*(?::|\s-)\s+(?=\S)")
SENTENCE_END = re.compile(r"(?<=[.!?])\s+|\s*\n+\s*")

NEAR_COPY = 0.90           # segment-to-segment cosine counted as "the same sentence"
MIN_HOSTS = 8              # a segment must recur in at least this many complaints
MAX_HOST_COHESION = 0.30   # mean cosine between the hosts' remaining text
MAX_COMPLAINTS = int(os.getenv("BOILERPLATE_MAX_COMPLAINTS", "2000"))
CHUNK = 512
PATH = os.getenv("BOILERPLATE_PATH", os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                                                  "boilerplate_segments.json"))

_saved = None              # (segments, unit embeddings) loaded from PATH


def split_segments(text):
    text = (text or "").strip()
    segments = []
    lead = LEAD_IN.match(text)
    if lead:
        segments.append(lead.group(1))
        text = text[lead.end():]
    segments += [s for s in SENTENCE_END.split(text) if s.strip()]
    return segments


def _encode(texts):
    from backend.services.embedding_service import model
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)
    return np.asarray(model.encode(texts, normalize_embeddings=True, show_progress_bar=False), dtype=np.float32)


def detect(texts):
    """Boilerplate segment texts of a corpus (same two passes as normalize.boilerplate_suppress)."""
    segs = [split_segments(t) for t in texts]
    flat = [(i, s) for i, ss in enumerate(segs) for s in ss]
    if not flat:
        return []
    emb = _encode([s for _, s in flat])
    owner = np.array([i for i, _ in flat])
    hosts_of = {}
    for start in range(0, len(flat), CHUNK):          # chunked: no full segment x segment matrix
        block = emb[start:start + CHUNK] @ emb.T
        for r, row in enumerate(block):
            a = start + r
            docs = set(owner[row >= NEAR_COPY].tolist()) | {flat[a][0]}
            if len(docs) >= MIN_HOSTS:
                hosts_of[a] = docs
    rest = [[] for _ in segs]
    for a, (i, s) in enumerate(flat):
        if a not in hosts_of:
            rest[i].append(s)
    has_rest = np.array([bool(r) for r in rest])
    rest_emb = np.zeros((len(segs), emb.shape[1]), dtype=np.float32)
    if has_rest.any():
        rest_emb[has_rest] = _encode([" ".join(r) for r in rest if r])
    boiler, checked = [], {}
    for a, docs in hosts_of.items():
        s = flat[a][1]
        key = s.lower().strip()
        if key not in checked:
            usable = [d for d in docs if has_rest[d]]
            if len(usable) < MIN_HOSTS // 2:
                checked[key] = None                       # cannot judge: keep
            else:
                e = rest_emb[usable]
                n = len(e)
                checked[key] = float(((e @ e.T).sum() - n) / (n * (n - 1)))
        if checked[key] is not None and checked[key] <= MAX_HOST_COHESION and key not in boiler:
            boiler.append(key)
    return boiler


def refresh(texts=None):
    """Re-detect boilerplate over the most recent stored complaints and save the list."""
    global _saved
    if texts is None:
        from backend.database.supabase import get_complaints
        rows = sorted(get_complaints(), key=lambda r: r.get("complaint_id") or 0)[-MAX_COMPLAINTS:]
        texts = [r.get("complaint_text") or "" for r in rows]
    found = detect(texts)
    os.makedirs(os.path.dirname(PATH), exist_ok=True)
    with open(PATH, "w", encoding="utf-8") as f:
        json.dump({"complaints_scanned": len(texts), "segments": found}, f, ensure_ascii=False, indent=1)
    _saved = None
    return {"complaints_scanned": len(texts), "boilerplate_segments": len(found)}


def _load():
    global _saved
    if _saved is None:
        segs = []
        if os.path.exists(PATH):
            try:
                segs = json.load(open(PATH, encoding="utf-8")).get("segments", [])
            except (OSError, ValueError):
                segs = []
        _saved = (segs, _encode(segs))
    return _saved


def strip(text):
    """Drop segments that are near-copies of saved boilerplate; keep at least one segment."""
    segs, bemb = _load()
    if not segs:
        return text
    parts = split_segments(text)
    if len(parts) < 2:
        return text
    keep = (_encode(parts) @ bemb.T).max(axis=1) < NEAR_COPY
    if not keep.any():
        return text
    return " ".join(p for p, k in zip(parts, keep) if k)
