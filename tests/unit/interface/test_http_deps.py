from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from src.interface.http.deps.actor import get_actor
from src.interface.http.deps.uow import get_uow


def test_get_actor_accepts_optional_org_id() -> None:
    user_id = uuid4()
    actor = asyncio.run(
        get_actor(
            x_user_id=user_id,
            x_is_admin=True,
            x_org_id="school-1",
        )
    )
    assert actor.user_id == user_id
    assert actor.is_admin is True
    assert actor.org_id == "school-1"


def test_get_uow_yields_uow_instance() -> None:
    async def _run():
        gen = get_uow()
        uow = await gen.__anext__()
        assert hasattr(uow, "user_repo")
        await gen.aclose()

    asyncio.run(_run())


def test_get_uow_rolls_back_on_exception(monkeypatch: pytest.MonkeyPatch) -> None:
    class _FakeUoW:
        rolled_back = False

        async def rollback(self) -> None:
            self.rolled_back = True

    monkeypatch.setattr(
        "src.interface.http.deps.uow.InMemoryUnitOfWork",
        _FakeUoW,
    )

    async def _run():
        gen = get_uow()
        uow = await gen.__anext__()
        with pytest.raises(RuntimeError):
            await gen.athrow(RuntimeError("boom"))
        assert uow.rolled_back is True

    asyncio.run(_run())


def test_main_exposes_app() -> None:
    from src.interface.http.main import app

    assert app is not None
