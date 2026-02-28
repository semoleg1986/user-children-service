from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class ChildCreated:
    user_id: UUID
    child_id: UUID
    occurred_at: datetime
    version_after: int
    status_after: str


@dataclass(frozen=True)
class ChildUpdated:
    user_id: UUID
    child_id: UUID
    occurred_at: datetime
    version_after: int
    status_after: str


@dataclass(frozen=True)
class ChildArchived:
    user_id: UUID
    child_id: UUID
    occurred_at: datetime
    version_after: int
    status_after: str


@dataclass(frozen=True)
class ChildRestored:
    user_id: UUID
    child_id: UUID
    occurred_at: datetime
    version_after: int
    status_after: str
