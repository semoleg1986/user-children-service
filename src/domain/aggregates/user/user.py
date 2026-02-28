from datetime import date, datetime, timezone
from typing import Any, Iterable
from uuid import UUID, uuid4

from src.domain.events import (
    ChildArchived,
    ChildCreated,
    ChildRestored,
    ChildUpdated,
    StoryAdded,
    UserCreated,
)
from src.domain.value_objects import ChildData, ChildStatus, StoryData, UserStatus

from .child import Child


class User:
    """
    Aggregate Root. Все операции над Child проходят через User.
    Инварианты: Child не существует вне User; один child_id не добавляется дважды.

    :param user_id: Уникальный идентификатор пользователя.
    :type user_id: UUID
    :param name: Имя пользователя.
    :type name: str
    """

    def __init__(
        self,
        user_id: UUID,
        name: str = "",
        *,
        status: UserStatus = UserStatus.ACTIVE,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
        version: int = 1,
        emit_created_event: bool = True,
    ) -> None:
        self._user_id = user_id
        self._name = name
        self._status = status if isinstance(status, UserStatus) else UserStatus(status)
        now = datetime.now(timezone.utc)
        self._created_at = created_at or now
        self._updated_at = updated_at or now
        self._version = version
        self._children: dict[UUID, Child] = {}
        self._events: list[Any] = []
        if emit_created_event:
            self._record_event(
                UserCreated(
                    user_id=self._user_id,
                    name=self._name,
                    occurred_at=now,
                    version_after=self._version,
                    status_after=self._status.value,
                )
            )

    @property
    def user_id(self) -> UUID:
        """
        Получить идентификатор пользователя.

        :return: UUID пользователя.
        :rtype: UUID
        """
        return self._user_id

    @property
    def name(self) -> str:
        """
        Получить имя пользователя.

        :return: Имя пользователя.
        :rtype: str
        """
        return self._name

    @property
    def children(self) -> Iterable[Child]:
        """
        Итератор по детям пользователя.

        :return: Итератор Child.
        :rtype: Iterable[Child]
        """
        return self._children.values()

    @property
    def status(self) -> UserStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    @property
    def version(self) -> int:
        return self._version

    def get_children(self) -> list[Child]:
        """Получить список активных (неархивированных) детей."""
        return [child for child in self._children.values() if not child.is_archived]

    def get_child(self, child_id: UUID) -> Child | None:
        """
        Получить ребёнка по id или None.

        :param child_id: Идентификатор ребёнка.
        :type child_id: UUID
        :return: Child или None.
        :rtype: Child | None
        """
        return self._children.get(child_id)

    def add_child(self, child_data: ChildData) -> Child:
        """
        Добавить ребёнка. Инвариант: child_id не дублируется.
        Возвращает созданного Child.

        :param child_data: Данные для создания ребёнка.
        :type child_data: ChildData
        :raises ValueError: Если child_id уже существует.
        :return: Созданный ребёнок.
        :rtype: Child
        """
        child_id = child_data.child_id or uuid4()
        if child_id in self._children:
            raise ValueError("Child with this id already exists")

        child = Child(
            child_id=child_id,
            name=child_data.name,
            birthdate=child_data.birthdate,
        )
        self._children[child_id] = child
        self._touch()
        self._record_event(
            ChildCreated(
                user_id=self._user_id,
                child_id=child.child_id,
                occurred_at=datetime.now(timezone.utc),
                version_after=self._version,
                status_after=child.status.value,
            )
        )
        return child

    def remove_child(self, child_id: UUID) -> None:
        """
        Совместимый alias: удалить ребёнка как soft-delete (archive).

        :param child_id: Идентификатор ребёнка.
        :type child_id: UUID
        :raises ValueError: Если ребёнок не найден.
        """
        self.archive_child(child_id)

    def archive_child(self, child_id: UUID) -> None:
        """
        Архивировать ребенка (soft-delete).

        :param child_id: Идентификатор ребенка.
        :type child_id: UUID
        :raises ValueError: Если ребенок не найден.
        """
        child = self._children.get(child_id)
        if child is None:
            raise ValueError("Child not found")
        child.archive()
        self._touch()
        self._record_event(
            ChildArchived(
                user_id=self._user_id,
                child_id=child_id,
                occurred_at=datetime.now(timezone.utc),
                version_after=self._version,
                status_after=ChildStatus.ARCHIVED.value,
            )
        )

    def restore_child(self, child_id: UUID) -> None:
        """
        Восстановить ребенка из архива.

        :param child_id: Идентификатор ребенка.
        :type child_id: UUID
        :raises ValueError: Если ребенок не найден.
        """
        child = self._children.get(child_id)
        if child is None:
            raise ValueError("Child not found")
        child.restore()
        self._touch()
        self._record_event(
            ChildRestored(
                user_id=self._user_id,
                child_id=child_id,
                occurred_at=datetime.now(timezone.utc),
                version_after=self._version,
                status_after=ChildStatus.ACTIVE.value,
            )
        )

    def update_child(
        self,
        child_id: UUID,
        *,
        name: str | None = None,
        birthdate: date | None = None,
    ) -> None:
        """
        Обновить данные ребёнка. Инварианты соблюдаются.
        Передаются только изменяемые поля (name и/или birthdate).

        :param child_id: Идентификатор ребёнка.
        :type child_id: UUID
        :param name: Новое имя.
        :type name: str | None
        :param birthdate: Новая дата рождения.
        :type birthdate: date | None
        :raises ValueError: Если ребёнок не найден.
        :raises TypeError: Если типы параметров неверны.
        """
        child = self._children.get(child_id)
        if not child:
            raise ValueError("Child not found")
        if child.is_archived:
            raise ValueError("Cannot update archived child")
        if name is not None:
            if not isinstance(name, str):
                raise TypeError("name must be str")
            setattr(child, "name", name)
        if birthdate is not None:
            if not isinstance(birthdate, date):
                raise TypeError("birthdate must be date")
            setattr(child, "birthdate", birthdate)
        child.updated_at = datetime.now(timezone.utc)
        child.version += 1
        self._touch()
        self._record_event(
            ChildUpdated(
                user_id=self._user_id,
                child_id=child_id,
                occurred_at=datetime.now(timezone.utc),
                version_after=self._version,
                status_after=child.status.value,
            )
        )

    def add_story(self, child_id: UUID, story_data: StoryData):
        child = self._children.get(child_id)
        if child is None:
            raise ValueError("Child not found")
        story = child.add_story(story_data)
        self._touch()
        self._record_event(
            StoryAdded(
                user_id=self._user_id,
                child_id=child_id,
                story_id=story.story_id,
                occurred_at=datetime.now(timezone.utc),
                version_after=self._version,
                status_after=child.status.value,
            )
        )
        return story

    def block(self) -> None:
        if self._status == UserStatus.BLOCKED:
            return
        self._status = UserStatus.BLOCKED
        self._touch()

    def unblock(self) -> None:
        if self._status == UserStatus.ACTIVE:
            return
        self._status = UserStatus.ACTIVE
        self._touch()

    def pull_events(self) -> list[Any]:
        events = list(self._events)
        self._events.clear()
        return events

    def _record_event(self, event: Any) -> None:
        self._events.append(event)

    def _touch(self) -> None:
        self._updated_at = datetime.now(timezone.utc)
        self._version += 1
