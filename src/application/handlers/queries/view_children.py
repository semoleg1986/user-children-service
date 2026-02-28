from src.application.errors import AccessDeniedError, NotFoundError
from src.application.queries.view_children import ViewChildrenQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.user import Child
from src.domain.policies.access_policy import AccessPolicy, Actor


async def handle(
    command: ViewChildrenQuery, *, uow: UnitOfWork, actor: Actor
) -> list[Child]:
    """
    Просмотреть список детей пользователя.

    :param command: Запрос на получение детей.
    :type command: ViewChildrenQuery
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises NotFoundError: Если пользователь не найден.
    :raises AccessDeniedError: Если доступ запрещён.
    :return: Список детей.
    :rtype: list[Child]
    """
    user = await uow.user_repo.get_by_id(command.user_id)
    if user is None:
        raise NotFoundError("User not found")

    if not AccessPolicy.can_view_children(actor, user):
        raise AccessDeniedError("Access denied")

    return user.get_children()
