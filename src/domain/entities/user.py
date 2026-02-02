from uuid import UUID
from typing import Iterable

from src.domain.entities.child import Child


class User:
    def __init__(self, user_id: UUID):
        self._id = user_id
        self._children: dict[UUID, Child] = {}

    @property
    def id(self) -> UUID:
        return self._id

    @property
    def children(self) -> Iterable[Child]:
        return self._children.values()

    # ====== Domain behavior ======

    def add_child(self, child: Child) -> None:
        if child.id in self._children:
            raise ValueError("Child already exists")

        self._children[child.id] = child

    def remove_child(self, child_id: UUID) -> None:
        if child_id not in self._children:
            raise ValueError("Child not found")

        del self._children[child_id]