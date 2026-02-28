from src.application.audit import emit_user_events
from src.application.commands.restore_child import RestoreChildCommand
from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import AccessPolicy, Actor


async def handle(
    command: RestoreChildCommand, *, uow: UnitOfWork, actor: Actor
) -> None:
    """
    Восстановить архивированного ребёнка.
    """
    user = await uow.user_repo.get_by_id(command.user_id)
    if user is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_restore_child(actor, user):
        raise AccessDeniedError("Access denied")

    try:
        user.restore_child(command.child_id)
    except ValueError as exc:
        raise InvariantViolationError(str(exc)) from exc

    await uow.user_repo.save(user)
    await emit_user_events(uow=uow, user=user, actor=actor)
    await uow.commit()
