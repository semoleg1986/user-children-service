"""In-memory реализация UserRepository для интеграционных тестов."""

from uuid import UUID

from src.domain.aggregates.user import User


class FakeUserRepository:
    """Репозиторий в памяти. Реализует UserRepository Protocol."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    def list_all(self) -> list[User]:
        return list(self._users.values())

    def save(self, user: User) -> None:
        self._users[user.user_id] = user

    def delete(self, user_id: UUID) -> None:
        self._users.pop(user_id, None)
