from __future__ import annotations

from uuid import UUID

from jwt import InvalidTokenError

from src.application.auth import AuthService
from src.domain.policies.access_policy import Actor
from src.infrastructure.clients.auth.jwks_cache import JWKSCache
from src.infrastructure.clients.auth.jwt_verifier import (
    is_admin_from_claims,
    verify_token_and_get_claims,
)
from src.infrastructure.clients.auth.settings import AuthSettings


class JwtAuthService(AuthService):
    def __init__(self, settings: AuthSettings, jwks_cache: JWKSCache) -> None:
        self._settings = settings
        self._jwks_cache = jwks_cache

    async def authenticate(self, token: str) -> Actor:
        claims = await verify_token_and_get_claims(
            token, settings=self._settings, jwks_cache=self._jwks_cache
        )

        subject = claims.get(self._settings.subject_claim)
        if not subject:
            raise InvalidTokenError("Token subject is missing")

        try:
            user_id = UUID(str(subject))
        except ValueError as exc:
            raise InvalidTokenError("Invalid token subject") from exc

        is_admin = is_admin_from_claims(claims, settings=self._settings)
        return Actor(user_id=user_id, is_admin=is_admin)
