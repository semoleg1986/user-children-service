from datetime import datetime
from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Query, Response, status

from src.application.commands import CreateUserCommand
from src.application.handlers import (
    handle_create_user,
    handle_view_audit_events,
    handle_view_children,
    handle_view_users,
)
from src.application.queries import (
    ViewAuditEventsQuery,
    ViewChildrenQuery,
    ViewUsersQuery,
)
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.interface.http.v1.error_responses import ADMIN_ERROR_RESPONSES
from src.interface.http.v1.schemas import (
    AuditEventResponse,
    ChildResponse,
    CreateUserRequest,
    UserResponse,
)

router = APIRouter(route_class=DishkaRoute)

ERROR_RESPONSES = ADMIN_ERROR_RESPONSES


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    responses=ERROR_RESPONSES,
)
async def create_user(
    body: CreateUserRequest,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
    response: Response,
):
    user = await handle_create_user(
        CreateUserCommand(user_id=body.user_id, name=body.name),
        uow=uow,
        actor=actor,
    )

    response.headers["Location"] = f"/v1/admin/users/{user.user_id}"
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        status=user.status.value,
        created_at=user.created_at,
        updated_at=user.updated_at,
        version=user.version,
    )


@router.get("/users", response_model=list[UserResponse], responses=ERROR_RESPONSES)
async def admin_view_users(
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
):
    users = await handle_view_users(ViewUsersQuery(), uow=uow, actor=actor)
    return [
        UserResponse(
            user_id=u.user_id,
            name=u.name,
            status=u.status.value,
            created_at=u.created_at,
            updated_at=u.updated_at,
            version=u.version,
        )
        for u in users
    ]


@router.get(
    "/users/{user_id}/children",
    response_model=list[ChildResponse],
    responses=ERROR_RESPONSES,
)
async def admin_view_children(
    user_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
):
    children = await handle_view_children(
        ViewChildrenQuery(user_id=user_id), uow=uow, actor=actor
    )

    return [
        ChildResponse(
            child_id=c.child_id,
            name=c.name,
            birthdate=c.birthdate,
            status=c.status.value,
            created_at=c.created_at,
            updated_at=c.updated_at,
            version=c.version,
        )
        for c in children
    ]


@router.get(
    "/audit/events",
    response_model=list[AuditEventResponse],
    responses=ERROR_RESPONSES,
)
async def admin_view_audit_events(
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
    actor_id: UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    target_type: str | None = Query(default=None),
    occurred_from: datetime | None = Query(default=None, alias="from"),
    occurred_to: datetime | None = Query(default=None, alias="to"),
):
    events = await handle_view_audit_events(
        ViewAuditEventsQuery(
            actor_id=actor_id,
            action=action,
            target_type=target_type,
            occurred_from=occurred_from,
            occurred_to=occurred_to,
        ),
        uow=uow,
        actor=actor,
    )
    return [
        AuditEventResponse(
            event_id=e.event_id,
            service=e.service,
            action=e.action,
            occurred_at=e.occurred_at,
            actor_id=e.actor_id,
            actor_role=e.actor_role,
            target_type=e.target_type,
            target_id=e.target_id,
            request_id=e.request_id,
            correlation_id=e.correlation_id,
            payload_before=e.payload_before,
            payload_after=e.payload_after,
            user_id=e.user_id,
            version_after=e.version_after,
            status_after=e.status_after,
        )
        for e in events
    ]
