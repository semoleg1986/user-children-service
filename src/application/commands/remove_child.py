from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RemoveChildCommand:
    user_id: UUID
    child_id: UUID
