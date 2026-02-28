from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class ChildData:
    """
    Данные для создания ребёнка.

    :param name: Имя ребёнка.
    :type name: str
    :param birthdate: Дата рождения.
    :type birthdate: date
    :param child_id: Идентификатор ребёнка (опционально).
    :type child_id: UUID | None
    """

    name: str
    birthdate: date
    child_id: UUID | None = None
