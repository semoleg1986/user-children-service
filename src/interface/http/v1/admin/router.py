from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from src.application.commands import CreateUserCommand
from src.application.handlers import (
    handle_create_user,
    handle_view_children,
    handle_view_users,
)
from src.application.queries import ViewChildrenQuery, ViewUsersQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.interface.http.v1.error_responses import ADMIN_ERROR_RESPONSES
from src.interface.http.v1.schemas import ChildResponse, CreateUserRequest, UserResponse

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
