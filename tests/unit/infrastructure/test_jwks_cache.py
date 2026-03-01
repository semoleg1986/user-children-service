from __future__ import annotations

import asyncio

import pytest

from src.infrastructure.clients.auth.jwks_cache import JWKSCache


class _FakeResponse:
    def __init__(self, payload):
        self._payload = payload

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class _FakeClient:
    calls = 0
    payload = {"keys": [{"kid": "k1"}]}

    def __init__(self, timeout: float):
        self.timeout = timeout

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def get(self, _url: str):
        _FakeClient.calls += 1
        return _FakeResponse(_FakeClient.payload)


def test_jwks_cache_uses_cached_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.infrastructure.clients.auth.jwks_cache.httpx.AsyncClient", _FakeClient
    )
    _FakeClient.calls = 0
    _FakeClient.payload = {"keys": [{"kid": "k1"}]}
    cache = JWKSCache("http://jwks.local", ttl_seconds=300)

    first = asyncio.run(cache.get_jwks())
    second = asyncio.run(cache.get_jwks())
    assert first == second
    assert _FakeClient.calls == 1


def test_jwks_cache_rejects_invalid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "src.infrastructure.clients.auth.jwks_cache.httpx.AsyncClient", _FakeClient
    )
    _FakeClient.calls = 0
    _FakeClient.payload = {"invalid": True}
    cache = JWKSCache("http://jwks.local", ttl_seconds=0)

    with pytest.raises(ValueError):
        asyncio.run(cache.get_jwks())
