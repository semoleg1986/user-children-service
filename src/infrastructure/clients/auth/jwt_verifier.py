from __future__ import annotations

from typing import Any, Iterable

import jwt
from jwt import InvalidTokenError

from src.infrastructure.clients.auth.jwks_cache import JWKSCache
from src.infrastructure.clients.auth.settings import AuthSettings


def _extract_claim_by_path(claims: dict[str, Any], path: str) -> Any:
    parts = [p for p in path.split(".") if p]
    current: Any = claims
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _extract_roles(claims: dict[str, Any], path: str) -> list[str]:
    current = _extract_claim_by_path(claims, path)

    if isinstance(current, list):
        return [str(r) for r in current]
    if isinstance(current, str):
        if " " in current:
            return [r for r in current.split(" ") if r]
        if "," in current:
            return [r for r in current.split(",") if r]
        return [current]
    return []


def extract_optional_claim(claims: dict[str, Any], *, claim_path: str) -> str | None:
    value = _extract_claim_by_path(claims, claim_path)
    if value is None:
        return None
    if isinstance(value, (str, int)):
        raw = str(value).strip()
        return raw or None
    return None


def _find_jwk(jwks: dict[str, Any], kid: str) -> dict[str, Any] | None:
    keys: Iterable[dict[str, Any]] = jwks.get("keys", [])
    for key in keys:
        if key.get("kid") == kid:
            return key
    return None


async def verify_token_and_get_claims(
    token: str, *, settings: AuthSettings, jwks_cache: JWKSCache
) -> dict[str, Any]:
    unverified_header = jwt.get_unverified_header(token)
    kid = unverified_header.get("kid")
    if not kid:
        raise InvalidTokenError("Token header missing kid")

    jwks = await jwks_cache.get_jwks()
    jwk = _find_jwk(jwks, kid)
    if jwk is None:
        raise InvalidTokenError("Unknown kid")

    public_key = jwt.algorithms.RSAAlgorithm.from_jwk(jwk)  # type: ignore[arg-type]

    claims = jwt.decode(
        token,
        key=public_key,
        algorithms=list(settings.algorithms),
        audience=settings.audience,
        issuer=settings.issuer,
        leeway=settings.clock_skew_seconds,
        options={"require": ["exp", settings.subject_claim, "iss", "aud"]},
    )

    return claims


def is_admin_from_claims(claims: dict[str, Any], *, settings: AuthSettings) -> bool:
    roles = _extract_roles(claims, settings.role_claim_path)
    return settings.admin_role in roles
