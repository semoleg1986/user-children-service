from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AuthSettings:
    jwks_url: str
    issuer: str
    audience: str
    algorithms: tuple[str, ...]
    role_claim_path: str
    admin_role: str
    subject_claim: str
    jwks_cache_ttl_seconds: int
    clock_skew_seconds: int


def load_auth_settings() -> AuthSettings:
    jwks_url = os.getenv("AUTH_JWKS_URL", "").strip()
    issuer = os.getenv("AUTH_ISSUER", "").strip()
    audience = os.getenv("AUTH_AUDIENCE", "").strip()
    algorithms_raw = os.getenv("AUTH_ALGORITHMS", "RS256").strip()
    role_claim_path = os.getenv("AUTH_ROLE_CLAIM", "roles").strip()
    admin_role = os.getenv("AUTH_ADMIN_ROLE", "admin").strip()
    subject_claim = os.getenv("AUTH_SUBJECT_CLAIM", "sub").strip()
    jwks_cache_ttl_seconds = int(os.getenv("AUTH_JWKS_CACHE_TTL", "300"))
    clock_skew_seconds = int(os.getenv("AUTH_CLOCK_SKEW", "30"))
    if jwks_cache_ttl_seconds < 0:
        raise ValueError("AUTH_JWKS_CACHE_TTL must be >= 0")
    if clock_skew_seconds < 0:
        raise ValueError("AUTH_CLOCK_SKEW must be >= 0")

    if not jwks_url or not issuer or not audience:
        raise ValueError(
            "Auth settings missing: AUTH_JWKS_URL, AUTH_ISSUER, AUTH_AUDIENCE"
        )

    algorithms = tuple(a for a in (s.strip() for s in algorithms_raw.split(",")) if a)
    if not algorithms:
        algorithms = ("RS256",)

    return AuthSettings(
        jwks_url=jwks_url,
        issuer=issuer,
        audience=audience,
        algorithms=algorithms,
        role_claim_path=role_claim_path,
        admin_role=admin_role,
        subject_claim=subject_claim,
        jwks_cache_ttl_seconds=jwks_cache_ttl_seconds,
        clock_skew_seconds=clock_skew_seconds,
    )
