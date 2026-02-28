from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class ViewChildrenQuery:
    user_id: UUID
