from dataclasses import dataclass
from uuid import UUID

from src.domain.value_objects import ChildData


@dataclass(frozen=True)
class AddChildCommand:
    user_id: UUID
    child_data: ChildData
