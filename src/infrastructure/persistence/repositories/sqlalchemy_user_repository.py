from __future__ import annotations

from typing import Dict
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.domain.aggregates.user import Child, Story, User
from src.domain.value_objects import ChildStatus, UserStatus
from src.infrastructure.persistence.sqlalchemy.models import (
    ChildModel,
    StoryModel,
    UserModel,
)


class SqlAlchemyUserRepository:
    def __init__(self, db_session: AsyncSession) -> None:
        self._db = db_session

    @staticmethod
    def _to_domain(model: UserModel) -> User:
        user = User(
            user_id=model.user_id,
            name=model.name,
            status=UserStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
            emit_created_event=False,
        )
        children_map: Dict[UUID, Child] = {}
        for child_model in model.children:
            child = Child(
                child_id=child_model.child_id,
                name=child_model.name,
                birthdate=child_model.birthdate,
                status=ChildStatus(child_model.status),
                created_at=child_model.created_at,
                updated_at=child_model.updated_at,
                version=child_model.version,
                archived_at=child_model.archived_at,
                _stories=[
                    Story(
                        story_id=story.story_id,
                        title=story.title,
                        content=story.content,
                        created_at=story.created_at,
                    )
                    for story in child_model.stories
                ],
            )
            children_map[child.child_id] = child

        user._children = children_map
        return user

    @staticmethod
    def _build_children_models(user: User) -> list[ChildModel]:
        result: list[ChildModel] = []
        for child in user.children:
            stories = [
                StoryModel(
                    story_id=s.story_id,
                    child_id=child.child_id,
                    title=s.title,
                    content=s.content,
                    created_at=s.created_at,
                )
                for s in child.get_stories()
            ]
            result.append(
                ChildModel(
                    child_id=child.child_id,
                    user_id=user.user_id,
                    name=child.name,
                    birthdate=child.birthdate,
                    status=child.status.value,
                    created_at=child.created_at,
                    updated_at=child.updated_at,
                    version=child.version,
                    archived_at=child.archived_at,
                    stories=stories,
                )
            )
        return result

    def _query_base(self):
        return select(UserModel).options(
            selectinload(UserModel.children).selectinload(ChildModel.stories)
        )

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = (
            await self._db.execute(
                self._query_base().where(UserModel.user_id == user_id)
            )
        ).scalar_one_or_none()
        if model is None:
            return None
        return self._to_domain(model)

    async def list_all(self) -> list[User]:
        rows = (await self._db.execute(self._query_base())).scalars().all()
        return [self._to_domain(item) for item in rows]

    async def save(self, user: User) -> None:
        model = await self._db.get(UserModel, user.user_id)
        if model is None:
            model = UserModel(
                user_id=user.user_id,
                name=user.name,
                status=user.status.value,
                created_at=user.created_at,
                updated_at=user.updated_at,
                version=user.version,
            )
            self._db.add(model)

        model.name = user.name
        model.status = user.status.value
        model.created_at = user.created_at
        model.updated_at = user.updated_at
        model.version = user.version
        model.children = self._build_children_models(user)

    async def delete(self, user_id: UUID) -> None:
        model = await self._db.get(UserModel, user_id)
        if model is not None:
            await self._db.delete(model)
