"""
Supabase Auth verification for FastAPI.

The frontend logs the user in with Supabase Auth and sends the access
token as:   Authorization: Bearer <token>

This module verifies that token on the server and returns the
authenticated user's Supabase UUID (the JWT "sub" claim). Endpoints must
use this UUID instead of any user_id sent by the frontend.

Verification
------------
- ES256 / RS256 tokens (Supabase "JWT signing keys", current default):
  checked against the project's public JWKS endpoint.
- HS256 tokens (legacy Supabase projects): checked with
  SUPABASE_JWT_SECRET, only if that variable is set.
- Always checked: signature, expiry, audience "authenticated",
  issuer "<SUPABASE_URL>/auth/v1", and presence of "sub".
"""

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()


# ==========================================================
# Configuration
# ==========================================================

AUDIENCE = "authenticated"
ASYMMETRIC_ALGORITHMS = ["ES256", "RS256"]
CLOCK_SKEW_SECONDS = 10

bearer_scheme = HTTPBearer(auto_error=False)


def _supabase_url() -> str:
    url = (os.getenv("SUPABASE_URL") or "").rstrip("/")

    if not url:
        raise RuntimeError("SUPABASE_URL is not set.")

    return url


def admin_auth_required() -> bool:
    """
    Whether /dashboard and /chat require an admin token.

    Off by default so the existing Streamlit dashboard (which sends no
    token) keeps working; turn on once the admin UI sends tokens.
    """
    return os.getenv("ADMIN_AUTH_REQUIRED", "false").strip().lower() in {
        "1", "true", "yes"
    }


@lru_cache(maxsize=1)
def _jwks_client() -> jwt.PyJWKClient:
    """
    Cached JWKS client; public keys are refetched every 10 minutes.
    """
    headers = {}
    api_key = os.getenv("SUPABASE_KEY")

    if api_key:
        headers["apikey"] = api_key

    return jwt.PyJWKClient(
        f"{_supabase_url()}/auth/v1/.well-known/jwks.json",
        cache_keys=True,
        lifespan=600,
        headers=headers,
        timeout=10,
    )


# ==========================================================
# Authenticated user
# ==========================================================

@dataclass(frozen=True)
class AuthUser:
    id: str
    email: Optional[str]
    role: str

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


def _unauthorized(detail: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": "Bearer"},
    )


def _signing_key(token: str, algorithm: str):
    if algorithm in ASYMMETRIC_ALGORITHMS:
        return _jwks_client().get_signing_key_from_jwt(token).key

    if algorithm == "HS256":
        secret = os.getenv("SUPABASE_JWT_SECRET")

        if secret:
            return secret

    raise _unauthorized("Unsupported token signing algorithm.")


def verify_token(token: str) -> AuthUser:
    """
    Verify a Supabase access token and return the user it belongs to.
    Raises HTTP 401 for any invalid token, 503 if keys can't be fetched.
    """
    try:
        algorithm = jwt.get_unverified_header(token).get("alg", "")
    except jwt.PyJWTError:
        raise _unauthorized("Malformed token.")

    try:
        claims = jwt.decode(
            token,
            _signing_key(token, algorithm),
            algorithms=[algorithm],
            audience=AUDIENCE,
            issuer=f"{_supabase_url()}/auth/v1",
            leeway=CLOCK_SKEW_SECONDS,
            options={"require": ["exp", "sub", "aud", "iss"]},
        )

    except jwt.ExpiredSignatureError:
        raise _unauthorized("Session expired. Please log in again.")

    except jwt.PyJWKClientConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable. Try again shortly.",
        )

    except jwt.PyJWTError:
        raise _unauthorized("Invalid token.")

    # App-level role lives in app_metadata, which users cannot edit.
    # (The top-level "role" claim is the Postgres role, "authenticated".)
    app_metadata = claims.get("app_metadata") or {}

    return AuthUser(
        id=claims["sub"],
        email=claims.get("email"),
        role=app_metadata.get("role") or "customer",
    )


# ==========================================================
# FastAPI dependencies
# ==========================================================

def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
) -> AuthUser:
    """
    Require a valid Supabase login. Use on customer endpoints.
    """
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise _unauthorized("Login required.")

    return verify_token(credentials.credentials)


def require_admin(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        bearer_scheme
    ),
) -> Optional[AuthUser]:
    """
    Require an admin login, when ADMIN_AUTH_REQUIRED is enabled.
    Admins are users whose app_metadata.role is "admin".
    """
    if not admin_auth_required():
        return None

    user = get_current_user(credentials)

    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required.",
        )

    return user
