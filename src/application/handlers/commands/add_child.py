from src.application.audit import emit_user_events
from src.application.commands.add_child import AddChildCommand
from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.user import Child
from src.domain.policies.access_policy import AccessPolicy, Actor


async def handle(command: AddChildCommand, *, uow: UnitOfWork, actor: Actor) -> Child:
    """
    Добавить ребёнка пользователю.

    :param command: Команда добавления ребёнка.
    :type command: AddChildCommand
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises NotFoundError: Если пользователь не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :raises InvariantViolationError: Если нарушены инварианты домена.
    :return: Созданный ребёнок.
    :rtype: Child
    """
    user = await uow.user_repo.get_by_id(command.user_id)
    if user is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_add_child(actor, user):
        raise AccessDeniedError("Access denied")

    try:
        child = user.add_child(command.child_data)
    except ValueError as exc:
        raise InvariantViolationError(str(exc)) from exc

    await uow.user_repo.save(user)
    await emit_user_events(uow=uow, user=user, actor=actor)
    await uow.commit()
    return child
