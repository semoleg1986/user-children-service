from src.application.audit import emit_user_events
from src.application.commands.add_story import AddStoryCommand
from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.user import Story
from src.domain.policies.access_policy import AccessPolicy, Actor


async def handle(command: AddStoryCommand, *, uow: UnitOfWork, actor: Actor) -> Story:
    """
    Добавить историю ребёнку.

    :param command: Команда добавления истории.
    :type command: AddStoryCommand
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises NotFoundError: Если пользователь или ребёнок не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :raises InvariantViolationError: Если нарушены инварианты домена.
    :return: Созданная история.
    :rtype: Story
    """
    user = await uow.user_repo.get_by_id(command.user_id)
    if user is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_add_story(actor, user):
        raise AccessDeniedError("Access denied")

    try:
        story = user.add_story(command.child_id, command.story_data)
    except ValueError as exc:
        if str(exc) == "Child not found":
            raise NotFoundError("Child not found") from exc
        raise InvariantViolationError(str(exc)) from exc

    await uow.user_repo.save(user)
    await emit_user_events(uow=uow, user=user, actor=actor)
    await uow.commit()
    return story
