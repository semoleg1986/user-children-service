from src.application.errors import AccessDeniedError
from src.application.queries.view_audit_events import ViewAuditEventsQuery
from src.application.unit_of_work import AuditEventRecord, UnitOfWork
from src.domain.policies.access_policy import Actor


async def handle(
    _query: ViewAuditEventsQuery, *, uow: UnitOfWork, actor: Actor
) -> list[AuditEventRecord]:
    if not actor.is_admin:
        raise AccessDeniedError("Access denied")
    events = await uow.audit_repo.list_all()

    if _query.actor_id is not None:
        events = [e for e in events if e.actor_id == _query.actor_id]
    if _query.action is not None:
        events = [e for e in events if e.action == _query.action]
    if _query.target_type is not None:
        events = [e for e in events if e.target_type == _query.target_type]
    if _query.occurred_from is not None:
        events = [e for e in events if e.occurred_at >= _query.occurred_from]
    if _query.occurred_to is not None:
        events = [e for e in events if e.occurred_at <= _query.occurred_to]

    return events
