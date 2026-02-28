from __future__ import annotations

from dataclasses import asdict
from uuid import uuid4

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
        payload_after = asdict(event)
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
