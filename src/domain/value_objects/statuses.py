from __future__ import annotations

from enum import StrEnum


class UserStatus(StrEnum):
    ACTIVE = "active"
    BLOCKED = "blocked"


class ChildStatus(StrEnum):
    ACTIVE = "active"
    ARCHIVED = "archived"
