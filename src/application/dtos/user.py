from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class StoryDTO:
    story_id: UUID
    title: str
    content: str


@dataclass(frozen=True)
class ChildDTO:
    child_id: UUID
    name: str
    birthdate: date
    stories: list[StoryDTO]


@dataclass(frozen=True)
class UserDTO:
    user_id: UUID
    name: str
    children: list[ChildDTO]
