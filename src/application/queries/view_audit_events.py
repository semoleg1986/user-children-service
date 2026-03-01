from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ViewAuditEventsQuery:
    """Запрос на получение списка audit-событий (admin-only)."""

    actor_id: UUID | None = None
    action: str | None = None
    target_type: str | None = None
    occurred_from: datetime | None = None
    occurred_to: datetime | None = None
