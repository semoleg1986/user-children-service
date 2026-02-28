from __future__ import annotations

import time
from typing import Any

import httpx


class JWKSCache:
    def __init__(self, jwks_url: str, ttl_seconds: int = 300) -> None:
        self._jwks_url = jwks_url
        self._ttl_seconds = ttl_seconds
        self._cached_at = 0.0
        self._jwks: dict[str, Any] | None = None

    async def get_jwks(self) -> dict[str, Any]:
        now = time.time()
        if self._jwks is not None and (now - self._cached_at) < self._ttl_seconds:
            return self._jwks

        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(self._jwks_url)
            resp.raise_for_status()
            jwks = resp.json()

        if "keys" not in jwks:
            raise ValueError("Invalid JWKS payload: missing 'keys'")

        self._jwks = jwks
        self._cached_at = now
        return jwks
