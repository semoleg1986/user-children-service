from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from src.application.unit_of_work import UnitOfWork
from src.infrastructure.persistence.repositories.sqlalchemy_audit_repository import (
    SqlAlchemyAuditRepository,
)
from src.infrastructure.persistence.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


class SqlAlchemyUnitOfWork(UnitOfWork):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self.user_repo = SqlAlchemyUserRepository(session)
        self.audit_repo = SqlAlchemyAuditRepository(session)

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()
