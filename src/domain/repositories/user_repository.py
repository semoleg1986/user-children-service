from typing import Protocol
from uuid import UUID

from src.domain.aggregates.user import User


class UserRepository(Protocol):
    """Репозиторий агрегата User."""

    def get_by_id(self, user_id: UUID) -> User | None:
        """Получить пользователя по id. None если не найден."""
        ...

    def save(self, user: User) -> None:
        """Сохранить агрегат User (вместе с Child)."""
        ...

    def delete(self, user_id: UUID) -> None:
        """Удалить пользователя по id."""
        ...
