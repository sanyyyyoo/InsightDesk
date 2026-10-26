"""LLM provider: judge decisions are cached by prompt; JSON mode is requested; failures are not cached."""

import json

import pytest

from backend.llm import provider


@pytest.fixture
def calls(monkeypatch, tmp_path):
    seen = []

    def fake(prompt, json_mode=False):
        seen.append((prompt, json_mode))
        if "broken" in prompt:
            return "not json"
        return json.dumps({"case": len(seen)})

    monkeypatch.setattr(provider, "generate_text", fake)
    monkeypatch.setattr(provider, "CACHE_PATH", str(tmp_path / "cache.jsonl"))
    monkeypatch.setattr(provider, "_cache", None)
    monkeypatch.setenv("LLM_CACHE", "1")
    return seen


def test_json_mode_is_requested(calls):
    provider.generate_json("Return JSON: {}")
    assert calls == [("Return JSON: {}", True)]


def test_cached_prompt_is_answered_once(calls):
    first = provider.generate_json("same prompt", cache=True)
    again = provider.generate_json("same prompt", cache=True)
    assert first == again == {"case": 1}
    assert len(calls) == 1


def test_cache_survives_a_restart(calls):
    provider.generate_json("same prompt", cache=True)
    provider._cache = None                                # as after a restart: reload from the file
    assert provider.generate_json("same prompt", cache=True) == {"case": 1}
    assert len(calls) == 1


def test_uncached_calls_always_reach_the_llm(calls):
    provider.generate_json("rca prompt")
    provider.generate_json("rca prompt")
    assert len(calls) == 2


def test_failed_answer_is_not_cached(calls):
    with pytest.raises(RuntimeError):
        provider.generate_json("broken prompt", cache=True)
    with pytest.raises(RuntimeError):
        provider.generate_json("broken prompt", cache=True)
    assert len(calls) == 2
