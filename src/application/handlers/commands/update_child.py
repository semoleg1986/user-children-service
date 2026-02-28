from src.application.audit import emit_user_events
from src.application.commands.update_child import UpdateChildCommand
from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import AccessPolicy, Actor


async def handle(command: UpdateChildCommand, *, uow: UnitOfWork, actor: Actor) -> None:
    """
    Обновить данные ребёнка.

    :param command: Команда обновления ребёнка.
    :type command: UpdateChildCommand
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises NotFoundError: Если пользователь не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :raises InvariantViolationError: Если нарушены инварианты домена.
    :return: None
    :rtype: None
    """
    user = await uow.user_repo.get_by_id(command.user_id)
    if user is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_update_child(actor, user):
        raise AccessDeniedError("Access denied")

    try:
        user.update_child(
            command.child_id,
            name=command.name,
            birthdate=command.birthdate,
        )
    except (ValueError, TypeError) as exc:
        raise InvariantViolationError(str(exc)) from exc

    await uow.user_repo.save(user)
    await emit_user_events(uow=uow, user=user, actor=actor)
    await uow.commit()
