from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.unit_of_work import AuditEventRecord
from src.infrastructure.persistence.sqlalchemy.models import AuditEventModel


class SqlAlchemyAuditRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    async def append(self, record: AuditEventRecord) -> None:
        self._db.add(
            AuditEventModel(
                event_id=record.event_id,
                service=record.service,
                action=record.action,
                occurred_at=record.occurred_at,
                actor_id=record.actor_id,
                actor_role=record.actor_role,
                target_type=record.target_type,
                target_id=record.target_id,
                request_id=record.request_id,
                correlation_id=record.correlation_id,
                payload_before=record.payload_before,
                payload_after=record.payload_after,
                user_id=record.user_id,
                version_after=record.version_after,
                status_after=record.status_after,
            )
        )

    async def list_all(self) -> list[AuditEventRecord]:
        rows = (
            await self._db.execute(
                select(AuditEventModel).order_by(AuditEventModel.occurred_at.desc())
            )
        ).scalars()
        return [
            AuditEventRecord(
                event_id=row.event_id,
                service=row.service,
                action=row.action,
                occurred_at=row.occurred_at,
                actor_id=row.actor_id,
                actor_role=row.actor_role,
                target_type=row.target_type,
                target_id=row.target_id,
                request_id=row.request_id,
                correlation_id=row.correlation_id,
                payload_before=row.payload_before,
                payload_after=row.payload_after,
                user_id=row.user_id,
                version_after=row.version_after,
                status_after=row.status_after,
            )
            for row in rows
        ]
