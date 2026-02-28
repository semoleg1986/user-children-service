"""Edge cases для Child и Story (Value Object)."""

from datetime import date
from uuid import uuid4

import pytest

from src.domain.aggregates.user import Child
from src.domain.value_objects import StoryData


@pytest.fixture
def child():
    return Child(child_id=uuid4(), name="Kid", birthdate=date(2020, 5, 15))


def test_get_stories_returns_copy(child):
    # Получаем истории, добавляем новую, старая коллекция не меняется
    story_data = StoryData(title="First", content="C1")
    child.add_story(story_data)
    stories_before = list(child.get_stories())
    child.add_story(StoryData(title="Second", content="C2"))
    stories_after = list(child.get_stories())
    assert len(stories_before) == 1
    assert len(stories_after) == 2


def test_story_immutable_after_creation(child):
    story = child.add_story(StoryData(title="Immutable", content="Content"))
    with pytest.raises(AttributeError):
        story.title = "Modified"
    with pytest.raises(AttributeError):
        story.content = "Modified"
