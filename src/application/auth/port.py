from __future__ import annotations

from typing import Protocol

from src.domain.policies.access_policy import Actor


class AuthService(Protocol):
    async def authenticate(self, token: str) -> Actor:
        """Validate token and return Actor."""
        ...
