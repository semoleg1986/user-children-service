from dataclasses import dataclass
from datetime import date
from uuid import UUID


@dataclass(frozen=True)
class UpdateChildCommand:
    user_id: UUID
    child_id: UUID
    name: str | None = None
    birthdate: date | None = None
