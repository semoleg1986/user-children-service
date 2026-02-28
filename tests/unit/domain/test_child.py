"""Unit-тесты сущности Child и Value Object Story."""

from datetime import date
from uuid import uuid4

import pytest

from src.domain.aggregates.user import Child
from src.domain.value_objects import StoryData


@pytest.fixture
def child_id():
    return uuid4()


@pytest.fixture
def child(child_id):
    return Child(
        child_id=child_id,
        name="Kid",
        birthdate=date(2020, 5, 15),
    )


class TestChildEntity:
    """Child: атрибуты, has_stories, get_stories."""

    def test_init_stores_attributes(self, child_id):
        c = Child(child_id=child_id, name="Alice", birthdate=date(2019, 1, 1))
        assert c.child_id == child_id
        assert c.name == "Alice"
        assert c.birthdate == date(2019, 1, 1)

    def test_has_stories_false_initially(self, child):
        assert child.has_stories() is False

    def test_get_stories_empty_initially(self, child):
        assert list(child.get_stories()) == []

    def test_archive_and_restore(self, child):
        child.archive()
        assert child.is_archived is True
        child.restore()
        assert child.is_archived is False


class TestChildAddStory:
    """Child.add_story: успех, дубликат story_id, возврат Story."""

    def test_add_story_returns_story_with_data(self, child):
        data = StoryData(title="First", content="Text")
        story = child.add_story(data)
        assert story.story_id is not None
        assert story.title == "First"
        assert story.content == "Text"
        assert story.created_at is not None

    def test_add_story_appears_in_get_stories(self, child):
        data = StoryData(title="T", content="C")
        story = child.add_story(data)
        stories = list(child.get_stories())
        assert len(stories) == 1
        assert stories[0].story_id == story.story_id

    def test_has_stories_true_after_add(self, child):
        child.add_story(StoryData(title="T", content="C"))
        assert child.has_stories() is True

    def test_add_story_with_explicit_story_id(self, child):
        sid = uuid4()
        data = StoryData(title="T", content="C", story_id=sid)
        story = child.add_story(data)
        assert story.story_id == sid

    def test_add_story_duplicate_story_id_raises(self, child):
        sid = uuid4()
        child.add_story(StoryData(title="A", content="C1", story_id=sid))
        with pytest.raises(ValueError, match="already exists"):
            child.add_story(StoryData(title="B", content="C2", story_id=sid))

    def test_add_story_to_archived_child_raises(self, child):
        child.archive()
        with pytest.raises(ValueError, match="archived"):
            child.add_story(StoryData(title="A", content="C1"))
