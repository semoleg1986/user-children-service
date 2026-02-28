from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects import StoryData


@dataclass(frozen=True)
class AddStoryCommand:
    user_id: UUID
    child_id: UUID
    story_data: StoryData
