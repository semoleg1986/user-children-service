"""Edge cases для User Aggregate Root."""

from datetime import date
from uuid import UUID, uuid4

import pytest

from src.domain.aggregates.user import User
from src.domain.value_objects import ChildData


@pytest.fixture
def user():
    return User(user_id=uuid4(), name="Owner")


def test_add_child_generates_uuid_if_none(user):
    data = ChildData(name="Kid", birthdate=date(2020, 5, 15), child_id=None)
    child = user.add_child(data)
    assert child.child_id is not None


def update_child(
    self, child_id: UUID, *, name: str | None = None, birthdate: object | None = None
) -> None:
    child = self._children.get(child_id)
    if not child:
        raise ValueError("Child not found")
    if name is not None:
        setattr(child, "name", name)
    if birthdate is not None:
        if not isinstance(birthdate, date):
            raise TypeError("birthdate must be date")
        setattr(child, "birthdate", birthdate)


def test_add_multiple_children_unique_ids(user):
    data1 = ChildData(name="Kid1", birthdate=date(2019, 1, 1))
    data2 = ChildData(name="Kid2", birthdate=date(2020, 2, 2))
    c1 = user.add_child(data1)
    c2 = user.add_child(data2)
    assert c1.child_id != c2.child_id
    assert len(user.get_children()) == 2


def test_add_multiple_stories_order(user):
    from src.domain.value_objects import StoryData

    data = ChildData(name="Kid", birthdate=date(2020, 5, 15))
    child = user.add_child(data)
    s1 = child.add_story(StoryData(title="S1", content="C1"))
    s2 = child.add_story(StoryData(title="S2", content="C2"))
    stories = list(child.get_stories())
    assert stories[0].story_id == s1.story_id
    assert stories[1].story_id == s2.story_id
