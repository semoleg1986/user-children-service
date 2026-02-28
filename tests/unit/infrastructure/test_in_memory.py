from __future__ import annotations

import asyncio
from uuid import uuid4

from src.domain.aggregates.user import User
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from src.infrastructure.persistence.uow.in_memory_uow import InMemoryUnitOfWork


def test_in_memory_user_repository_crud() -> None:
    repo = InMemoryUserRepository()
    user_id = uuid4()
    user = User(user_id=user_id, name="Alice")

    assert asyncio.run(repo.get_by_id(user_id)) is None
    asyncio.run(repo.save(user))
    assert asyncio.run(repo.get_by_id(user_id)) is user

    asyncio.run(repo.delete(user_id))
    assert asyncio.run(repo.get_by_id(user_id)) is None


def test_in_memory_user_repository_list_all() -> None:
    repo = InMemoryUserRepository()
    user1 = User(user_id=uuid4(), name="U1")
    user2 = User(user_id=uuid4(), name="U2")

    asyncio.run(repo.save(user1))
    asyncio.run(repo.save(user2))

    users = asyncio.run(repo.list_all())
    assert {u.user_id for u in users} == {user1.user_id, user2.user_id}


def test_in_memory_uow_commit_and_rollback() -> None:
    uow = InMemoryUnitOfWork()
    assert uow.committed is False
    assert uow.rolled_back is False

    asyncio.run(uow.commit())
    assert uow.committed is True

    asyncio.run(uow.rollback())
    assert uow.rolled_back is True
