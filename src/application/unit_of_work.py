from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from src.domain.aggregates.user import User


class AsyncUserRepository(Protocol):
    """Async repository contract for User aggregate."""

    async def get_by_id(self, user_id) -> User | None:  # type: ignore[override]
        ...

    async def list_all(self) -> list[User]:
        """Список всех пользователей."""
        ...

    async def save(self, user: User) -> None:
        ...

    async def delete(self, user_id) -> None:  # type: ignore[override]
        ...


@dataclass(frozen=True)
class AuditEventRecord:
    event_id: UUID
    service: str
    action: str
    occurred_at: datetime
    actor_id: UUID
    actor_role: str
    target_type: str
    target_id: UUID
    request_id: str | None
    correlation_id: str | None
    payload_before: dict
    payload_after: dict
    user_id: UUID | None
    version_after: int | None
    status_after: str | None


class AsyncAuditRepository(Protocol):
    async def append(self, record: AuditEventRecord) -> None:
        ...

    async def list_all(self) -> list[AuditEventRecord]:
        ...


class UnitOfWork(Protocol):
    """Async UoW contract for application layer."""

    user_repo: AsyncUserRepository
    audit_repo: AsyncAuditRepository

    async def commit(self) -> None:
        """Commit the current transaction."""

    async def rollback(self) -> None:
        """Rollback the current transaction."""

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.rollback()
