from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class RestoreChildCommand:
    user_id: UUID
    child_id: UUID
