from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class StoryAdded:
    user_id: UUID
    child_id: UUID
    story_id: UUID
    occurred_at: datetime
    version_after: int
    status_after: str
