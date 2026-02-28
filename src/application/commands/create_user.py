from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateUserCommand:
    user_id: UUID
    name: str = ""
