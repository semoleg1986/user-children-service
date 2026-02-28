from uuid import UUID

from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Response, status

from src.application.commands import (
    AddChildCommand,
    AddStoryCommand,
    CreateUserCommand,
    RemoveChildCommand,
    RestoreChildCommand,
    UpdateChildCommand,
)
from src.application.handlers import (
    handle_add_child,
    handle_add_story,
    handle_create_user,
    handle_remove_child,
    handle_restore_child,
    handle_update_child,
    handle_view_children,
)
from src.application.queries import ViewChildrenQuery
from src.application.unit_of_work import UnitOfWork
from src.domain.policies.access_policy import Actor
from src.domain.value_objects import ChildData, StoryData
from src.interface.http.v1.error_responses import USER_ERROR_RESPONSES
from src.interface.http.v1.schemas import (
    ChildCreateRequest,
    ChildResponse,
    ChildUpdateRequest,
    SelfCreateUserRequest,
    StoryCreateRequest,
    StoryResponse,
    UserResponse,
)

router = APIRouter(route_class=DishkaRoute)

ERROR_RESPONSES = USER_ERROR_RESPONSES


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserResponse,
    responses=ERROR_RESPONSES,
)
async def self_create_user(
    body: SelfCreateUserRequest,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
    response: Response,
):
    user = await handle_create_user(
        CreateUserCommand(user_id=actor.user_id, name=body.name),
        uow=uow,
        actor=actor,
    )

    response.headers["Location"] = f"/v1/user/users/{user.user_id}"
    return UserResponse(
        user_id=user.user_id,
        name=user.name,
        status=user.status.value,
        created_at=user.created_at,
        updated_at=user.updated_at,
        version=user.version,
    )


@router.get(
    "/users/{user_id}/children",
    response_model=list[ChildResponse],
    responses=ERROR_RESPONSES,
)
async def view_children(
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


@router.post(
    "/users/{user_id}/children",
    status_code=status.HTTP_201_CREATED,
    response_model=ChildResponse,
    responses=ERROR_RESPONSES,
)
async def add_child(
    user_id: UUID,
    body: ChildCreateRequest,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
    response: Response,
):
    child = await handle_add_child(
        AddChildCommand(
            user_id=user_id,
            child_data=ChildData(
                name=body.name,
                birthdate=body.birthdate,
                child_id=body.child_id,
            ),
        ),
        uow=uow,
        actor=actor,
    )

    response.headers["Location"] = f"/v1/user/users/{user_id}/children/{child.child_id}"
    return ChildResponse(
        child_id=child.child_id,
        name=child.name,
        birthdate=child.birthdate,
        status=child.status.value,
        created_at=child.created_at,
        updated_at=child.updated_at,
        version=child.version,
    )


@router.patch(
    "/users/{user_id}/children/{child_id}",
    responses=ERROR_RESPONSES,
)
async def update_child(
    user_id: UUID,
    child_id: UUID,
    body: ChildUpdateRequest,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
):
    await handle_update_child(
        UpdateChildCommand(
            user_id=user_id,
            child_id=child_id,
            name=body.name,
            birthdate=body.birthdate,
        ),
        uow=uow,
        actor=actor,
    )

    return {"status": "ok"}


@router.delete(
    "/users/{user_id}/children/{child_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses=ERROR_RESPONSES,
)
async def remove_child(
    user_id: UUID,
    child_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
):
    await handle_remove_child(
        RemoveChildCommand(user_id=user_id, child_id=child_id),
        uow=uow,
        actor=actor,
    )


@router.post(
    "/users/{user_id}/children/{child_id}/restore",
    responses=ERROR_RESPONSES,
)
async def restore_child(
    user_id: UUID,
    child_id: UUID,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
):
    await handle_restore_child(
        RestoreChildCommand(user_id=user_id, child_id=child_id),
        uow=uow,
        actor=actor,
    )

    return {"status": "ok"}


@router.post(
    "/users/{user_id}/children/{child_id}/stories",
    status_code=status.HTTP_201_CREATED,
    response_model=StoryResponse,
    responses=ERROR_RESPONSES,
)
async def add_story(
    user_id: UUID,
    child_id: UUID,
    body: StoryCreateRequest,
    actor: FromDishka[Actor],
    uow: FromDishka[UnitOfWork],
    response: Response,
):
    story = await handle_add_story(
        AddStoryCommand(
            user_id=user_id,
            child_id=child_id,
            story_data=StoryData(
                title=body.title, content=body.content, story_id=body.story_id
            ),
        ),
        uow=uow,
        actor=actor,
    )

    response.headers[
        "Location"
    ] = f"/v1/user/users/{user_id}/children/{child_id}/stories/{story.story_id}"
    return StoryResponse(
        story_id=story.story_id, title=story.title, content=story.content
    )
