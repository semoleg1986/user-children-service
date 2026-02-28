from __future__ import annotations

from typing import AsyncIterator

from src.application.unit_of_work import UnitOfWork
from src.infrastructure.persistence.uow.in_memory_uow import InMemoryUnitOfWork


async def get_uow() -> AsyncIterator[UnitOfWork]:
    uow = InMemoryUnitOfWork()
    try:
        yield uow
    except Exception:
        await uow.rollback()
        raise
