from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class Story:
    """
    Story — запись/история ребёнка (Value Object).
    Принадлежит Child, immutable после создания.

    :param story_id: Идентификатор истории.
    :type story_id: UUID
    :param title: Заголовок истории.
    :type title: str
    :param content: Текст истории.
    :type content: str
    :param created_at: Дата создания.
    :type created_at: datetime
    """

    story_id: UUID
    title: str
    content: str
    created_at: datetime
