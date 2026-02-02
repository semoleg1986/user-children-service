from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class Child:
    id: UUID
    name: str