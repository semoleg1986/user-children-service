from src.application.errors import AccessDeniedError
from src.application.queries.view_users import ViewUsersQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.aggregates.user import User
from src.domain.policies.access_policy import Actor


async def handle(
    _query: ViewUsersQuery, *, uow: UnitOfWork, actor: Actor
) -> list[User]:
    """
    Получить список всех пользователей (admin-only).

    :param _query: Запрос на получение пользователей.
    :type _query: ViewUsersQuery
    :param uow: Unit of Work.
    :type uow: UnitOfWork
    :param actor: Актор запроса.
    :type actor: Actor
    :raises AccessDeniedError: Если актор не админ.
    :return: Список пользователей.
    :rtype: list[User]
    """
    if not actor.is_admin:
        raise AccessDeniedError("Access denied")
    return await uow.user_repo.list_all()
