from __future__ import annotations

from typing import Dict
from uuid import UUID

from src.domain.aggregates.user import User


class InMemoryUserRepository:
    """In-memory repository for User aggregate."""

    def __init__(self) -> None:
        self._users: Dict[UUID, User] = {}

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def list_all(self) -> list[User]:
        return list(self._users.values())

    async def save(self, user: User) -> None:
        self._users[user.user_id] = user

    async def delete(self, user_id: UUID) -> None:
        self._users.pop(user_id, None)
