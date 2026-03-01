from __future__ import annotations

from uuid import uuid4

import pytest
from jwt import InvalidTokenError

from src.infrastructure.clients.auth.jwt_auth_service import JwtAuthService
from src.infrastructure.clients.auth.jwt_verifier import (
    extract_optional_claim,
    is_admin_from_claims,
)
from src.infrastructure.clients.auth.settings import AuthSettings


def _settings() -> AuthSettings:
    return AuthSettings(
        jwks_url="http://jwks.local",
        issuer="auth-service",
        audience="user-children-service",
        algorithms=("RS256",),
        role_claim_path="roles",
        admin_role="admin",
        subject_claim="sub",
        org_claim="org_id",
        jwks_cache_ttl_seconds=300,
        clock_skew_seconds=30,
    )


class _DummyJWKS:
    async def get_jwks(self):  # pragma: no cover - not used directly in this unit test
        return {"keys": []}


def test_extract_optional_claim_supports_nested_path() -> None:
    claims = {"org": {"id": "school-1"}}
    assert extract_optional_claim(claims, claim_path="org.id") == "school-1"
    assert extract_optional_claim(claims, claim_path="org.missing") is None


def test_is_admin_from_claims_handles_csv_roles() -> None:
    claims = {"roles": "user,admin"}
    assert is_admin_from_claims(claims, settings=_settings()) is True


@pytest.mark.asyncio
async def test_jwt_auth_service_reads_optional_org_id(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    subject = str(uuid4())

    async def _fake_verify(_token: str, *, settings, jwks_cache):
        return {"sub": subject, "roles": ["user"], "org_id": "school-7"}

    monkeypatch.setattr(
        "src.infrastructure.clients.auth.jwt_auth_service.verify_token_and_get_claims",
        _fake_verify,
    )

    svc = JwtAuthService(_settings(), _DummyJWKS())
    actor = await svc.authenticate("token")
    assert str(actor.user_id) == subject
    assert actor.org_id == "school-7"
    assert actor.is_admin is False


@pytest.mark.asyncio
async def test_jwt_auth_service_rejects_invalid_subject(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def _fake_verify(_token: str, *, settings, jwks_cache):
        return {"sub": "not-a-uuid", "roles": ["admin"]}

    monkeypatch.setattr(
        "src.infrastructure.clients.auth.jwt_auth_service.verify_token_and_get_claims",
        _fake_verify,
    )

    svc = JwtAuthService(_settings(), _DummyJWKS())
    with pytest.raises(InvalidTokenError):
        await svc.authenticate("token")
