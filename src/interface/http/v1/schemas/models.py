from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class CreateUserRequest(BaseModel):
    user_id: UUID
    name: str = ""


class UserResponse(BaseModel):
    user_id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime
    version: int


class SelfCreateUserRequest(BaseModel):
    name: str = ""


class ChildCreateRequest(BaseModel):
    name: str
    birthdate: date
    child_id: UUID | None = None


class ChildUpdateRequest(BaseModel):
    name: str | None = None
    birthdate: date | None = None


class ChildResponse(BaseModel):
    child_id: UUID
    name: str
    birthdate: date
    status: str
    created_at: datetime
    updated_at: datetime
    version: int


class StoryCreateRequest(BaseModel):
    title: str
    content: str
    story_id: UUID | None = None


class StoryResponse(BaseModel):
    story_id: UUID
    title: str
    content: str


class ProblemDetails(BaseModel):
    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
    request_id: str | None = None


class AuditEventResponse(BaseModel):
    event_id: UUID
    service: str
    action: str
    occurred_at: datetime
    actor_id: UUID
    actor_role: str
    target_type: str
    target_id: UUID
    request_id: str | None
    correlation_id: str | None
    payload_before: dict[str, object]
    payload_after: dict[str, object]
    user_id: UUID | None
    version_after: int | None
    status_after: str | None
