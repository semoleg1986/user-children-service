from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class StoryData:
    """
    Данные для создания истории ребёнка.

    :param title: Заголовок истории.
    :type title: Str
    :param content: Текст истории.
    :type content: str
    :param story_id: Идентификатор истории (опционально).
    :type story_id: UUID | None
    """

    title: str
    content: str
    story_id: UUID | None = None  # если None — генерируется в Child.add_story
