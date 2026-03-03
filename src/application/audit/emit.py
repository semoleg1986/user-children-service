from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from uuid import UUID, uuid4

from src.application.unit_of_work import AuditEventRecord, UnitOfWork
from src.domain.aggregates.user import User
from src.domain.policies.access_policy import Actor


def _action_for_event_name(name: str) -> str:
    # ChildArchived -> child.archived
    if not name:
        return "unknown.changed"
    parts = []
    chunk = name[0]
    for char in name[1:]:
        if char.isupper():
            parts.append(chunk)
            chunk = char
        else:
            chunk += char
    parts.append(chunk)
    if len(parts) >= 2:
        return f"{parts[0].lower()}.{ '_'.join(p.lower() for p in parts[1:]) }"
    return f"{name.lower()}.changed"


def _to_jsonable(value):
    """Преобразовать вложенные структуры в JSON-совместимый формат."""
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, datetime | date):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    return value


async def emit_user_events(
    *,
    uow: UnitOfWork,
    user: User,
    actor: Actor,
    request_id: str | None = None,
    correlation_id: str | None = None,
    service: str = "user-children-service",
) -> None:
    for event in user.pull_events():
        payload_after = _to_jsonable(asdict(event))
        target_id = getattr(event, "child_id", None) or getattr(event, "user_id", None)
        target_type = "child" if getattr(event, "child_id", None) else "user"
        record = AuditEventRecord(
            event_id=uuid4(),
            service=service,
            action=_action_for_event_name(type(event).__name__),
            occurred_at=getattr(event, "occurred_at"),
            actor_id=actor.user_id,
            actor_role="admin" if actor.is_admin else "user",
            target_type=target_type,
            target_id=target_id,
            request_id=request_id,
            correlation_id=correlation_id,
            payload_before={},
            payload_after=payload_after,
            user_id=getattr(event, "user_id", None),
            version_after=getattr(event, "version_after", None),
            status_after=getattr(event, "status_after", None),
        )
        await uow.audit_repo.append(record)
