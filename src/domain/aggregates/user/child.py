from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Iterable
from uuid import UUID, uuid4

from src.domain.value_objects import ChildStatus, StoryData

from .story import Story


@dataclass
class Child:
    """
    Сущность ребёнка. Принадлежит User, не существует без него.
    Все изменения — через User.

    :param child_id: Идентификатор ребёнка.
    :type child_id: UUID
    :param name: Имя ребёнка.
    :type name: str
    :param birthdate: Дата рождения.
    :type birthdate: date
    """

    child_id: UUID
    name: str
    birthdate: date
    status: ChildStatus = ChildStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: int = 1
    archived_at: datetime | None = None
    _stories: list[Story] | None = None

    def __post_init__(self) -> None:
        if self._stories is None:
            object.__setattr__(self, "_stories", [])
        if isinstance(self.status, str):
            object.__setattr__(self, "status", ChildStatus(self.status))

    def has_stories(self) -> bool:
        """
        Есть ли у ребёнка хотя бы одна история (для инварианта 5).

        :return: True, если есть истории.
        :rtype: bool
        """
        return len(self._stories) > 0

    @property
    def is_archived(self) -> bool:
        """Признак архивированного ребенка."""
        return self.status == ChildStatus.ARCHIVED

    def archive(self) -> None:
        """Soft-delete: перевести ребенка в archived."""
        if self.is_archived:
            return
        self.status = ChildStatus.ARCHIVED
        self.archived_at = datetime.now(timezone.utc)
        self._touch()

    def restore(self) -> None:
        """Восстановить ребенка из archived."""
        if not self.is_archived:
            return
        self.status = ChildStatus.ACTIVE
        self.archived_at = None
        self._touch()

    def _touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1

    def add_story(self, story_data: StoryData) -> Story:
        """
        Добавить историю. Инвариант: нет дубликата story_id.

        :param story_data: Данные для создания истории.
        :type story_data: StoryData
        :raises ValueError: Если story_id уже существует.
        :return: Созданная история.
        :rtype: Story
        """
        if self.is_archived:
            raise ValueError("Cannot add story to archived child")
        story_id = story_data.story_id or uuid4()
        for s in self._stories:
            if s.story_id == story_id:
                raise ValueError("Story with this id already exists")
        story = Story(
            story_id=story_id,
            title=story_data.title,
            content=story_data.content,
            created_at=datetime.now(timezone.utc),
        )
        self._stories.append(story)
        self._touch()
        return story

    def get_stories(self) -> Iterable[Story]:
        """
        Получить все истории.

        :return: Список историй.
        :rtype: Iterable[Story]
        """
        return list(self._stories)
