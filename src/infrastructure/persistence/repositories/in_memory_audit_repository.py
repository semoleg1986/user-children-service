from __future__ import annotations

from src.application.unit_of_work import AuditEventRecord


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self._events: list[AuditEventRecord] = []

    async def append(self, record: AuditEventRecord) -> None:
        self._events.append(record)

    async def list_all(self) -> list[AuditEventRecord]:
        return list(self._events)
