from __future__ import annotations

from uuid import UUID

from fastapi import Header

from src.domain.policies.access_policy import Actor


async def get_actor(
    x_user_id: UUID = Header(..., alias="X-User-Id"),
    x_is_admin: bool = Header(False, alias="X-Is-Admin"),
) -> Actor:
    return Actor(user_id=x_user_id, is_admin=x_is_admin)
