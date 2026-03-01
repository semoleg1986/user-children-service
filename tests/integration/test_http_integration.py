from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives import serialization
from fastapi.testclient import TestClient
from jwt.utils import base64url_encode

_PRIVATE_KEY_PEM = """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCDKb9C9nyWeCJI
e6KiODzDUvkJb+TTCxRLMjzudPojp9G8X7U7BbuGThRI1VfrHhwGHyCwOXiIlHzI
SBvLurRl2RZd1KC40ryxs4I9QtFTevjaGNmvVUz+PLV6H0n5TxUnnLrvLtTFN8ft
B8jpaCQpSGnqfH6fbuCDBhBN/6hb/+QXBIv2HvbYmEcCxZZkalQoHFUJaxHS3bbM
uP2FHLLCsPsiaQhFlfBwtjyA1iM9ekUJOzgQyvkILwuVTq6w4JolnMD3I9uT87Tc
m+7OH3vUBzyzireVefTrUX/1lCuHML9/T5AdpRNVkivlvIGDHwwNTdLCgK9DiSJO
jDdfekadAgMBAAECggEAEfHW+TwcUQDIHfcOSdfcVlPGfxhIK+h+4wfRRsWJyHGI
FBfbBWN0I7yQcWOA1wnER0EgeYOvXi5EgSk+ZknZrvp7oSQ7RfYM+1nmFmgLF/sB
y2Lte1u2AC2BnZ7kwb9kU0pR1/HmCcJnL6JqRiapld1SolJch4cFn99nQSiaWdWv
NK1u0UDDEXnoVkshY3sRVijjmM+rRx4E0+gg9BnsXKuwq35J6TDqvLcfaPN4DHIw
VLyv0UtkmZyr9jf5gC+Ywg9CFhUzenPtms9SHuf2aq9Fcy/UlN/8iT043wXsgZzM
GdiTiMihGoJ4tkQGDWV4J+F3fV0dsw2l+0lT3455sQKBgQC4QK/rjGnBU0xN9rdV
nFeri0KCVh2L50pRjXV7ZWHtUts3Y5Yb9AtcStuKR1/PnxluuAzcCD0clgUnz/X8
P2B1oD4C0bYpu9evwn2MbY/nEfbIIZIITqyn9PVqROt7VL/P1NFy8z74sm3tuQXb
u5Eit2UsyzYfggI+Q5bxGp0qEQKBgQC2PMxJQQ4sbWgv44jtM3EtL2Y7aEiEVaaD
JlqPfJNSPGe10kEgp23fSNdNV7zHCmOVoO6d3604iBVb7QjuoBgGJugtrhqAQMDf
7aUK1sMB5i8HudQWl2we92/yQCopUZM2nMaUwfPmtl5ugW7wQidnJRxaBheaOO8G
OIghu8cnzQKBgE5DA7Y8bQs103pmKhdOEhsGStjLtT8gnfun51fjh0Xj5MNRJIh5
D35DOZ8xk+u/e3EA8k1fnn2O51+ywJxFWzZ7Ovu9ke+GHyZDqUpFm1Md2UHGqJ2o
tUOeE8PwxEkdhV/E2LZHxd6jA3hvF6Lut8YUOgBdzH5znXpPAUUl9c3RAoGAZg/m
2Z/1sCwWDbwBE9ebqxLAzsS42GSfvRPd5D6Aw63Q56O5lfAvOL4y1r4sm8zVuRdI
jGKZQO/2BmXaespuqgNgRTUc4ndhjggqRsfAr2+bJ1iLz5s+kplBuQr2ke195Tgo
f2egkbXRbVJQL37dUocWOdTvow//zhwbIclo4IECgYBlWuOctCrLeySRyCuv67C3
w/003GfxSH1+qkqk9TKsC1Gv1iNdkhMHFxsYn0+0aSKQTDXI82HovIQkDi+VUzC/
DZfk3y56ovo2yvv4mXsWW15AiyfVfBOqAnWAdN372FTIPlCZE8SWwG+Yz/Xc2Aa/
zFp2Vnlc5VgdGdtNpvVJdg==
-----END PRIVATE KEY-----"""

_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAgym/QvZ8lngiSHuiojg8
w1L5CW/k0wsUSzI87nT6I6fRvF+1OwW7hk4USNVX6x4cBh8gsDl4iJR8yEgby7q0
ZdkWXdSguNK8sbOCPULRU3r42hjZr1VM/jy1eh9J+U8VJ5y67y7UxTfH7QfI6Wgk
KUhp6nx+n27ggwYQTf+oW//kFwSL9h722JhHAsWWZGpUKBxVCWsR0t22zLj9hRyy
wrD7ImkIRZXwcLY8gNYjPXpFCTs4EMr5CC8LlU6usOCaJZzA9yPbk/O03Jvuzh97
1Ac8s4q3lXn061F/9ZQrhzC/f0+QHaUTVZIr5byBgx8MDU3SwoCvQ4kiTow3X3pG
nQIDAQAB
-----END PUBLIC KEY-----"""


def _compute_kid(jwk: dict[str, str]) -> str:
    thumbprint = json.dumps(
        {k: jwk[k] for k in sorted(jwk) if k != "kid"},
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    import hashlib

    return base64url_encode(hashlib.sha256(thumbprint).digest()).decode("utf-8")


def _build_jwks_with_kid() -> dict[str, list[dict[str, str]]]:
    public_key = serialization.load_pem_public_key(_PUBLIC_KEY_PEM.encode("utf-8"))
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(public_key))
    jwk["kid"] = _compute_kid(jwk)
    return {"keys": [jwk]}


def _issue_access_token(user_id: str, roles: list[str], kid: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "roles": roles,
        "iss": "auth-service",
        "aud": "user-children-service",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
    }
    return jwt.encode(
        payload,
        _PRIVATE_KEY_PEM,
        algorithm="RS256",
        headers={"kid": kid},
    )


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("AUTH_JWKS_URL", "http://jwks.local")
    monkeypatch.setenv("AUTH_ISSUER", "auth-service")
    monkeypatch.setenv("AUTH_AUDIENCE", "user-children-service")
    monkeypatch.setenv("AUTH_ALGORITHMS", "RS256")

    from src.interface.http.app import create_app

    app = create_app()
    return TestClient(app)


@pytest.fixture()
def jwks(monkeypatch: pytest.MonkeyPatch):
    jwks_payload = _build_jwks_with_kid()

    async def _fake_get_jwks(self):
        return jwks_payload

    monkeypatch.setattr(
        "src.infrastructure.clients.auth.jwks_cache.JWKSCache.get_jwks",
        _fake_get_jwks,
        raising=True,
    )
    return jwks_payload


def test_full_flow(client: TestClient, jwks) -> None:
    user_id = str(uuid4())
    kid = jwks["keys"][0]["kid"]
    token = _issue_access_token(user_id=user_id, roles=["user"], kid=kid)

    create_user = client.post(
        "/v1/user/users",
        json={"name": "Oleg"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_user.status_code == 201

    add_child = client.post(
        f"/v1/user/users/{user_id}/children",
        json={"name": "Kid", "birthdate": "2020-05-15"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert add_child.status_code == 201

    list_children = client.get(
        f"/v1/user/users/{user_id}/children",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_children.status_code == 200
    assert len(list_children.json()) == 1


def test_admin_can_read_audit_events(client: TestClient, jwks) -> None:
    user_id = str(uuid4())
    admin_id = str(uuid4())
    kid = jwks["keys"][0]["kid"]
    user_token = _issue_access_token(user_id=user_id, roles=["user"], kid=kid)
    admin_token = _issue_access_token(user_id=admin_id, roles=["admin"], kid=kid)

    create_user = client.post(
        "/v1/user/users",
        json={"name": "Oleg"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert create_user.status_code == 201

    response = client.get(
        "/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) >= 1
    assert payload[0]["service"] == "user-children-service"
    assert payload[0]["actor_id"] == user_id


def test_non_admin_cannot_read_audit_events(client: TestClient, jwks) -> None:
    user_id = str(uuid4())
    kid = jwks["keys"][0]["kid"]
    token = _issue_access_token(user_id=user_id, roles=["user"], kid=kid)

    response = client.get(
        "/v1/admin/audit/events",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


def test_admin_can_filter_audit_events(client: TestClient, jwks) -> None:
    user_id = str(uuid4())
    admin_id = str(uuid4())
    kid = jwks["keys"][0]["kid"]
    user_token = _issue_access_token(user_id=user_id, roles=["user"], kid=kid)
    admin_token = _issue_access_token(user_id=admin_id, roles=["admin"], kid=kid)

    client.post(
        "/v1/user/users",
        json={"name": "Oleg"},
        headers={"Authorization": f"Bearer {user_token}"},
    )
    client.post(
        f"/v1/user/users/{user_id}/children",
        json={"name": "Kid", "birthdate": "2020-05-15"},
        headers={"Authorization": f"Bearer {user_token}"},
    )

    by_action = client.get(
        "/v1/admin/audit/events",
        params={"action": "child.created"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert by_action.status_code == 200
    action_events = by_action.json()
    assert len(action_events) >= 1
    assert all(event["action"] == "child.created" for event in action_events)

    by_actor = client.get(
        "/v1/admin/audit/events",
        params={"actor_id": user_id},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert by_actor.status_code == 200
    actor_events = by_actor.json()
    assert len(actor_events) >= 2
    assert all(event["actor_id"] == user_id for event in actor_events)

    by_time = client.get(
        "/v1/admin/audit/events",
        params={"from": "2099-01-01T00:00:00+00:00"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert by_time.status_code == 200
    assert by_time.json() == []

    by_to = client.get(
        "/v1/admin/audit/events",
        params={"to": "2099-01-01T00:00:00+00:00"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert by_to.status_code == 200
    assert len(by_to.json()) >= 2


def test_admin_audit_events_invalid_datetime_returns_422(
    client: TestClient, jwks
) -> None:
    admin_id = str(uuid4())
    kid = jwks["keys"][0]["kid"]
    admin_token = _issue_access_token(user_id=admin_id, roles=["admin"], kid=kid)

    response = client.get(
        "/v1/admin/audit/events",
        params={"from": "not-a-datetime"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response.status_code == 422
