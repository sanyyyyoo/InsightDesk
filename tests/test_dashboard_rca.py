"""
On-demand RCA generation endpoint (POST /dashboard/cases/{id}/rca).

No Supabase, Pinecone or LLM access: get_case and the generator are
replaced with fakes.
"""

from dataclasses import dataclass

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.routers import dashboard


@dataclass
class FakeRCA:
    probable_cause: str
    severity: str


@pytest.fixture
def client(monkeypatch):
    calls = []

    def fake_generate(case_id, force_regenerate=False):
        calls.append((case_id, force_regenerate))
        if case_id == 13:
            raise RuntimeError("LLM response missing required fields")
        if case_id == 14:
            raise ValueError("provider down")
        return FakeRCA(probable_cause="SMS gateway failing", severity="HIGH")

    monkeypatch.setattr(dashboard, "get_case", lambda cid: None if cid == 404 else {"case_id": cid})
    app = FastAPI()
    app.include_router(dashboard.router)
    app.dependency_overrides[dashboard.get_rca_generator] = lambda: fake_generate
    c = TestClient(app)
    c.calls = calls
    return c


def test_generates_and_returns_rca(client):
    r = client.post("/dashboard/cases/7/rca")
    assert r.status_code == 200
    assert r.json() == {"probable_cause": "SMS gateway failing", "severity": "HIGH"}
    assert client.calls == [(7, False)]


def test_force_flag_is_passed_through(client):
    client.post("/dashboard/cases/7/rca?force=true")
    assert client.calls == [(7, True)]


def test_unknown_case_is_404_and_never_calls_the_llm(client):
    r = client.post("/dashboard/cases/404/rca")
    assert r.status_code == 404
    assert client.calls == []


def test_unusable_llm_output_is_502(client):
    assert client.post("/dashboard/cases/13/rca").status_code == 502


def test_other_failures_are_500_without_leaking_details(client):
    r = client.post("/dashboard/cases/14/rca")
    assert r.status_code == 500
    assert "provider down" not in r.text


def test_get_does_not_generate(client):
    # only POST generates; there is no GET route at this path
    assert client.get("/dashboard/cases/7/rca").status_code == 405
    assert client.calls == []
