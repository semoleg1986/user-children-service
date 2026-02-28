from dataclasses import dataclass


@dataclass(frozen=True)
class ViewUsersQuery:
    """Запрос на получение списка пользователей."""
