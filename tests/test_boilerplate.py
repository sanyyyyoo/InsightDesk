"""Boilerplate suppression (backend/services/boilerplate.py) with a fake encoder: same text -> same
vector, different texts -> orthogonal vectors. The real-encoder check against the tested E4a output
(488/488 identical on the synthetic set) is test_boilerplate_equivalence.py."""

import sys
import types

import numpy as np
import pytest


class FakeModel:
    def __init__(self):
        self.ids = {}

    def encode(self, texts, normalize_embeddings=True, show_progress_bar=False):
        out = np.zeros((len(texts), 384), dtype=np.float32)
        for k, t in enumerate(texts):
            out[k, self.ids.setdefault(t.lower().strip(), len(self.ids) % 384)] = 1.0
        return out


@pytest.fixture
def bp(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "backend.services.embedding_service", types.SimpleNamespace(model=FakeModel()))
    from backend.services import boilerplate
    monkeypatch.setattr(boilerplate, "PATH", str(tmp_path / "boilerplate.json"))
    monkeypatch.setattr(boilerplate, "_saved", None)
    return boilerplate


def corpus():
    greeting = "Hi team, please help."
    return [f"{greeting} Problem number {k} happens on screen {k}." for k in range(10)]


def test_greeting_in_unrelated_complaints_is_dropped(bp):
    assert bp.refresh(corpus())["boilerplate_segments"] == 1
    assert bp.strip("Hi team, please help. The export button does nothing.") == "The export button does nothing."


def test_at_least_one_segment_is_kept(bp):
    bp.refresh(corpus())
    assert bp.strip("Hi team, please help.") == "Hi team, please help."


def test_no_saved_list_leaves_text_unchanged(bp):
    text = "Hi team, please help. The export button does nothing."
    assert bp.strip(text) == text


def test_rare_segment_is_not_boilerplate(bp):
    texts = corpus()[:5]                       # only 5 hosts < MIN_HOSTS (8)
    assert bp.refresh(texts)["boilerplate_segments"] == 0
