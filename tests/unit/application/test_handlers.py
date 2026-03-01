from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

import pytest

from src.application.commands import (
    AddChildCommand,
    AddStoryCommand,
    CreateUserCommand,
    RemoveChildCommand,
    RestoreChildCommand,
    UpdateChildCommand,
)
from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.application.handlers import (
    handle_add_child,
    handle_add_story,
    handle_create_user,
    handle_remove_child,
    handle_restore_child,
    handle_update_child,
    handle_view_children,
    handle_view_users,
)
from src.application.queries import ViewChildrenQuery, ViewUsersQuery
from src.application.unit_of_work import AuditEventRecord
from src.domain.aggregates.user import User
from src.domain.policies.access_policy import Actor
from src.domain.value_objects import ChildData, StoryData


@dataclass
class InMemoryUserRepo:
    users: dict[UUID, User]

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self.users.get(user_id)

    async def list_all(self) -> list[User]:
        return list(self.users.values())

    async def save(self, user: User) -> None:
        self.users[user.user_id] = user

    async def delete(self, user_id: UUID) -> None:
        self.users.pop(user_id, None)


class InMemoryUoW:
    def __init__(self, repo: InMemoryUserRepo) -> None:
        self.user_repo = repo
        self.audit_repo = self
        self.audit_events: list[AuditEventRecord] = []
        self.committed = False
        self.rolled_back = False

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True

    async def append(self, record: AuditEventRecord) -> None:
        self.audit_events.append(record)

    async def list_all(self) -> list[AuditEventRecord]:
        return list(self.audit_events)


@pytest.fixture()
def admin_actor() -> Actor:
    return Actor(user_id=uuid4(), is_admin=True)


@pytest.fixture()
def user_actor() -> Actor:
    return Actor(user_id=uuid4(), is_admin=False)


@pytest.fixture()
def repo() -> InMemoryUserRepo:
    return InMemoryUserRepo(users={})


@pytest.fixture()
def uow(repo: InMemoryUserRepo) -> InMemoryUoW:
    return InMemoryUoW(repo)


def test_create_user_user_cannot_create_other(
    uow: InMemoryUoW, user_actor: Actor
) -> None:
    other_user_id = uuid4()
    with pytest.raises(AccessDeniedError):
        asyncio.run(
            handle_create_user(
                CreateUserCommand(user_id=other_user_id, name="Other"),
                uow=uow,
                actor=user_actor,
            )
        )


def test_create_user_success(uow: InMemoryUoW, admin_actor: Actor) -> None:
    user_id = uuid4()
    user = asyncio.run(
        handle_create_user(
            CreateUserCommand(user_id=user_id, name="Test"),
            uow=uow,
            actor=admin_actor,
        )
    )

    assert user.user_id == user_id
    assert asyncio.run(uow.user_repo.get_by_id(user_id)) is user
    assert uow.committed is True
    assert any(e.action == "user.created" for e in uow.audit_events)


def test_create_user_self_success(uow: InMemoryUoW, user_actor: Actor) -> None:
    user = asyncio.run(
        handle_create_user(
            CreateUserCommand(user_id=user_actor.user_id, name="Self"),
            uow=uow,
            actor=user_actor,
        )
    )

    assert user.user_id == user_actor.user_id
    assert asyncio.run(uow.user_repo.get_by_id(user_actor.user_id)) is user
    assert uow.committed is True


def test_add_child_user_not_found(uow: InMemoryUoW, admin_actor: Actor) -> None:
    child_data = ChildData(name="Kid", birthdate=date(2020, 5, 15))
    with pytest.raises(NotFoundError):
        asyncio.run(
            handle_add_child(
                AddChildCommand(user_id=uuid4(), child_data=child_data),
                uow=uow,
                actor=admin_actor,
            )
        )


def test_add_child_access_denied(uow: InMemoryUoW, user_actor: Actor) -> None:
    other_user = User(user_id=uuid4(), name="Other")
    asyncio.run(uow.user_repo.save(other_user))

    child_data = ChildData(name="Kid", birthdate=date(2020, 5, 15))
    with pytest.raises(AccessDeniedError):
        asyncio.run(
            handle_add_child(
                AddChildCommand(user_id=other_user.user_id, child_data=child_data),
                uow=uow,
                actor=user_actor,
            )
        )


def test_add_child_success(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    asyncio.run(uow.user_repo.save(owner))

    child_data = ChildData(name="Kid", birthdate=date(2020, 5, 15))
    child = asyncio.run(
        handle_add_child(
            AddChildCommand(user_id=owner.user_id, child_data=child_data),
            uow=uow,
            actor=user_actor,
        )
    )

    assert child in owner.get_children()
    assert uow.committed is True
    assert any(e.action == "child.created" for e in uow.audit_events)


def test_remove_child_archives_child(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    child = owner.add_child(ChildData(name="Kid", birthdate=date(2020, 5, 15)))
    asyncio.run(uow.user_repo.save(owner))

    asyncio.run(
        handle_remove_child(
            RemoveChildCommand(user_id=owner.user_id, child_id=child.child_id),
            uow=uow,
            actor=user_actor,
        )
    )
    assert owner.get_child(child.child_id) is not None
    assert owner.get_child(child.child_id).is_archived is True
    assert owner.get_children() == []


def test_restore_child_success(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    child = owner.add_child(ChildData(name="Kid", birthdate=date(2020, 5, 15)))
    child.archive()
    asyncio.run(uow.user_repo.save(owner))

    asyncio.run(
        handle_restore_child(
            RestoreChildCommand(user_id=owner.user_id, child_id=child.child_id),
            uow=uow,
            actor=user_actor,
        )
    )
    assert owner.get_child(child.child_id).is_archived is False
    assert any(e.action == "child.restored" for e in uow.audit_events)


def test_update_child_not_found(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    asyncio.run(uow.user_repo.save(owner))

    with pytest.raises(InvariantViolationError):
        asyncio.run(
            handle_update_child(
                UpdateChildCommand(user_id=owner.user_id, child_id=uuid4(), name="New"),
                uow=uow,
                actor=user_actor,
            )
        )


def test_add_story_child_not_found(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    asyncio.run(uow.user_repo.save(owner))

    with pytest.raises(NotFoundError):
        asyncio.run(
            handle_add_story(
                AddStoryCommand(
                    user_id=owner.user_id,
                    child_id=uuid4(),
                    story_data=StoryData(title="S", content="C"),
                ),
                uow=uow,
                actor=user_actor,
            )
        )


def test_add_story_access_denied(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=uuid4(), name="Other")
    child = owner.add_child(ChildData(name="Kid", birthdate=date(2020, 5, 15)))
    asyncio.run(uow.user_repo.save(owner))

    with pytest.raises(AccessDeniedError):
        asyncio.run(
            handle_add_story(
                AddStoryCommand(
                    user_id=owner.user_id,
                    child_id=child.child_id,
                    story_data=StoryData(title="S", content="C"),
                ),
                uow=uow,
                actor=user_actor,
            )
        )


def test_add_story_success(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    child = owner.add_child(ChildData(name="Kid", birthdate=date(2020, 5, 15)))
    asyncio.run(uow.user_repo.save(owner))

    story = asyncio.run(
        handle_add_story(
            AddStoryCommand(
                user_id=owner.user_id,
                child_id=child.child_id,
                story_data=StoryData(title="S", content="C"),
            ),
            uow=uow,
            actor=user_actor,
        )
    )
    assert story.title == "S"
    assert uow.committed is True
    assert any(e.action == "story.added" for e in uow.audit_events)


def test_add_story_invariant_violation_for_archived_child(
    uow: InMemoryUoW, user_actor: Actor
) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    child = owner.add_child(ChildData(name="Kid", birthdate=date(2020, 5, 15)))
    child.archive()
    asyncio.run(uow.user_repo.save(owner))

    with pytest.raises(InvariantViolationError):
        asyncio.run(
            handle_add_story(
                AddStoryCommand(
                    user_id=owner.user_id,
                    child_id=child.child_id,
                    story_data=StoryData(title="S", content="C"),
                ),
                uow=uow,
                actor=user_actor,
            )
        )


def test_view_children_success(uow: InMemoryUoW, user_actor: Actor) -> None:
    owner = User(user_id=user_actor.user_id, name="Owner")
    active = owner.add_child(ChildData(name="Kid", birthdate=date(2020, 5, 15)))
    archived = owner.add_child(ChildData(name="Kid2", birthdate=date(2021, 1, 1)))
    archived.archive()
    asyncio.run(uow.user_repo.save(owner))

    children = asyncio.run(
        handle_view_children(
            ViewChildrenQuery(user_id=owner.user_id),
            uow=uow,
            actor=user_actor,
        )
    )

    assert len(children) == 1
    assert children[0].child_id == active.child_id


def test_view_users_admin_only(uow: InMemoryUoW, user_actor: Actor) -> None:
    asyncio.run(uow.user_repo.save(User(user_id=user_actor.user_id, name="Owner")))

    with pytest.raises(AccessDeniedError):
        asyncio.run(handle_view_users(ViewUsersQuery(), uow=uow, actor=user_actor))


def test_view_users_success(uow: InMemoryUoW, admin_actor: Actor) -> None:
    u1 = User(user_id=uuid4(), name="U1")
    u2 = User(user_id=uuid4(), name="U2")
    asyncio.run(uow.user_repo.save(u1))
    asyncio.run(uow.user_repo.save(u2))

    users = asyncio.run(handle_view_users(ViewUsersQuery(), uow=uow, actor=admin_actor))
    assert {u.user_id for u in users} == {u1.user_id, u2.user_id}
