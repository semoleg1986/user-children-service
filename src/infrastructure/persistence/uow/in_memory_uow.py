from __future__ import annotations

from src.application.unit_of_work import UnitOfWork
from src.infrastructure.persistence.repositories.in_memory_audit_repository import (
    InMemoryAuditRepository,
)
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)


class InMemoryUnitOfWork(UnitOfWork):
    def __init__(
        self,
        user_repo: InMemoryUserRepository | None = None,
        audit_repo: InMemoryAuditRepository | None = None,
    ) -> None:
        self.user_repo = user_repo or InMemoryUserRepository()
        self.audit_repo = audit_repo or InMemoryAuditRepository()
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True
