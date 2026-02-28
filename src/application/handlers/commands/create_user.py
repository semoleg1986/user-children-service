from src.application.audit import emit_user_events
from src.application.commands.create_user import CreateUserCommand
from src.application.errors import AccessDeniedError, InvariantViolationError
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.user import User
from src.domain.policies.access_policy import AccessPolicy, Actor


async def handle(command: CreateUserCommand, *, uow: UnitOfWork, actor: Actor) -> User:
    """
    Создать пользователя.

    :param command: Команда создания пользователя.
    :type command: CreateUserCommand
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises AccessDeniedError: Если доступ запрещён.
    :raises InvariantViolationError: Если пользователь уже существует.
    :return: Созданный пользователь.
    :rtype: User
    """
    if not AccessPolicy.can_manage_user(actor, command.user_id):
        raise AccessDeniedError("Access denied")

    existing = await uow.user_repo.get_by_id(command.user_id)
    if existing is not None:
        raise InvariantViolationError("User already exists")

    user = User(user_id=command.user_id, name=command.name)
    await uow.user_repo.save(user)
    await emit_user_events(uow=uow, user=user, actor=actor)
    await uow.commit()
    return user
