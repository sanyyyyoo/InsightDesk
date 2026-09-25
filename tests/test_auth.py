"""
Tests for Supabase token verification and the protected /analyze route.

No network, database, Pinecone or ML models are used: tokens are signed
with a locally generated EC key that stands in for the project's JWKS,
and the complaint pipeline is replaced with a recorder.

Run:  .venv\\Scripts\\python -m pytest tests -q
"""

import time
import uuid

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from backend import auth
from backend.routers import complaints


SUPABASE_URL = "https://testproject.supabase.co"
ISSUER = f"{SUPABASE_URL}/auth/v1"

PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())
OTHER_PRIVATE_KEY = ec.generate_private_key(ec.SECP256R1())

VALID_TEXT = "The ticket dashboard takes over a minute to load every morning."


# ==========================================================
# Helpers
# ==========================================================

def make_token(
    sub=None,
    key=PRIVATE_KEY,
    algorithm="ES256",
    expires_in=3600,
    **overrides,
):
    now = int(time.time())
    claims = {
        "sub": sub or str(uuid.uuid4()),
        "aud": "authenticated",
        "iss": ISSUER,
        "iat": now,
        "exp": now + expires_in,
        "email": "customer@example.com",
        "role": "authenticated",
        "app_metadata": {"provider": "email"},
    }
    claims.update(overrides)
    claims = {k: v for k, v in claims.items() if v is not None}

    return jwt.encode(claims, key, algorithm=algorithm, headers={"kid": "test"})


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


class FakeSigningKey:
    key = PRIVATE_KEY.public_key()


class FakeJWKSClient:
    def get_signing_key_from_jwt(self, token):
        return FakeSigningKey()


class Recorder:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def __call__(self, complaint):
        if self.fail:
            raise RuntimeError("pinecone timeout at 10.0.0.5")
        self.calls.append(complaint)
        return {"complaint_id": 1, "case_id": 7, "is_duplicate": False,
                "status": "New case created"}


@pytest.fixture(autouse=True)
def test_env(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", SUPABASE_URL)
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    monkeypatch.setenv("ADMIN_AUTH_REQUIRED", "false")
    monkeypatch.setattr(auth, "_jwks_client", lambda: FakeJWKSClient())


@pytest.fixture
def pipeline():
    return Recorder()


@pytest.fixture
def client(pipeline):
    app = FastAPI()
    app.include_router(complaints.router)

    @app.get("/admin-only", dependencies=[Depends(auth.require_admin)])
    def admin_only():
        return {"ok": True}

    app.dependency_overrides[complaints.get_pipeline] = lambda: pipeline

    return TestClient(app)


def submit(client, token=None, **body):
    body.setdefault("complaint_text", VALID_TEXT)
    headers = bearer(token) if token else {}
    return client.post("/analyze", json=body, headers=headers)


# ==========================================================
# Login required
# ==========================================================

def test_no_token_is_rejected(client, pipeline):
    response = submit(client)

    assert response.status_code == 401
    assert response.json()["detail"] == "Login required."
    assert pipeline.calls == []


def test_malformed_token_is_rejected(client, pipeline):
    response = submit(client, token="not-a-jwt")

    assert response.status_code == 401
    assert pipeline.calls == []


def test_expired_token_is_rejected(client, pipeline):
    response = submit(client, token=make_token(expires_in=-3600))

    assert response.status_code == 401
    assert "expired" in response.json()["detail"].lower()
    assert pipeline.calls == []


@pytest.mark.parametrize("overrides", [
    {"aud": "anon"},                                   # wrong audience
    {"iss": "https://evil.supabase.co/auth/v1"},       # other project
    {"sub": None, "aud": None},                        # anon-key style token
])
def test_wrong_claims_are_rejected(client, pipeline, overrides):
    response = submit(client, token=make_token(**overrides))

    assert response.status_code == 401
    assert pipeline.calls == []


def test_token_signed_by_another_key_is_rejected(client, pipeline):
    response = submit(client, token=make_token(key=OTHER_PRIVATE_KEY))

    assert response.status_code == 401
    assert pipeline.calls == []


def test_hs256_token_rejected_without_legacy_secret(client, pipeline):
    token = make_token(key="guessable-secret-value-32-bytes!!", algorithm="HS256")

    assert submit(client, token=token).status_code == 401
    assert pipeline.calls == []


def test_hs256_token_accepted_with_legacy_secret(client, pipeline, monkeypatch):
    secret = "legacy-project-jwt-secret-32bytes"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    user_id = str(uuid.uuid4())

    response = submit(client, token=make_token(sub=user_id, key=secret, algorithm="HS256"))

    assert response.status_code == 200
    assert pipeline.calls[0].user_id == user_id


def test_jwks_unreachable_returns_503(client, pipeline, monkeypatch):
    class DownJWKS:
        def get_signing_key_from_jwt(self, token):
            raise jwt.PyJWKClientConnectionError("connection refused")

    monkeypatch.setattr(auth, "_jwks_client", lambda: DownJWKS())

    assert submit(client, token=make_token()).status_code == 503
    assert pipeline.calls == []


# ==========================================================
# user_id comes only from the token
# ==========================================================

def test_valid_token_submits_with_token_user_id(client, pipeline):
    user_id = str(uuid.uuid4())

    response = submit(client, token=make_token(sub=user_id), rating=2, product="Helpdesk")

    assert response.status_code == 200
    assert response.json()["case_id"] == 7

    complaint = pipeline.calls[0]
    assert complaint.user_id == user_id
    assert complaint.complaint_text == VALID_TEXT
    assert complaint.rating == 2
    assert complaint.product == "Helpdesk"
    assert complaint.source == "web_portal"
    assert complaint.is_synthetic is False


def test_user_id_in_body_is_ignored(client, pipeline):
    real_user = str(uuid.uuid4())

    response = submit(
        client,
        token=make_token(sub=real_user),
        user_id="someone-else",
        source="spoofed",
        is_synthetic=True,
    )

    assert response.status_code == 200
    complaint = pipeline.calls[0]
    assert complaint.user_id == real_user
    assert complaint.source == "web_portal"
    assert complaint.is_synthetic is False


# ==========================================================
# Input validation
# ==========================================================

@pytest.mark.parametrize("text", [
    "please help me",          # only 1 word left after stop words
    "hello thanks please!!!",  # nothing left after cleaning
    "            !!!!!!!!!!",  # whitespace and symbols
])
def test_too_vague_after_cleaning_is_400(client, pipeline, text):
    response = submit(client, token=make_token(), complaint_text=text)

    assert response.status_code == 400
    assert pipeline.calls == []


@pytest.mark.parametrize("body", [
    {"complaint_text": "too short"},                 # < 10 characters
    {"complaint_text": "x" * 5001},                  # > 5000 characters
    {"complaint_text": VALID_TEXT, "rating": 6},     # rating out of 1-5
    {},                                              # missing text
])
def test_invalid_body_is_422(client, pipeline, body):
    response = client.post("/analyze", json=body, headers=bearer(make_token()))

    assert response.status_code == 422
    assert pipeline.calls == []


def test_pipeline_error_hides_internal_details(monkeypatch):
    app = FastAPI()
    app.include_router(complaints.router)
    app.dependency_overrides[complaints.get_pipeline] = lambda: Recorder(fail=True)

    response = submit(TestClient(app), token=make_token())

    assert response.status_code == 500
    assert "10.0.0.5" not in response.text
    assert "pinecone" not in response.text.lower()


# ==========================================================
# Admin protection
# ==========================================================

def test_admin_routes_open_when_flag_off(client):
    assert client.get("/admin-only").status_code == 200


def test_admin_routes_need_login_when_flag_on(client, monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_REQUIRED", "true")

    assert client.get("/admin-only").status_code == 401


def test_customer_cannot_use_admin_routes(client, monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_REQUIRED", "true")

    response = client.get("/admin-only", headers=bearer(make_token()))

    assert response.status_code == 403


def test_admin_can_use_admin_routes(client, monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_REQUIRED", "true")
    token = make_token(app_metadata={"provider": "email", "role": "admin"})

    assert client.get("/admin-only", headers=bearer(token)).status_code == 200


def test_user_editable_metadata_cannot_grant_admin(client, monkeypatch):
    monkeypatch.setenv("ADMIN_AUTH_REQUIRED", "true")
    token = make_token(user_metadata={"role": "admin"})

    assert client.get("/admin-only", headers=bearer(token)).status_code == 403
