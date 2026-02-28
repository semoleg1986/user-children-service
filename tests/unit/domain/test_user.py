"""Unit-тесты агрегата User (Aggregate Root)."""

from datetime import date
from uuid import uuid4

import pytest

from src.domain.aggregates.user import User
from src.domain.value_objects import ChildData, StoryData


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def user(user_id):
    return User(user_id=user_id, name="Test User")


@pytest.fixture
def child_data():
    return ChildData(name="Kid", birthdate=date(2020, 5, 15))


class TestUserAggregate:
    """User: создание, атрибуты, get_children, get_child."""

    def test_init_has_user_id_and_name(self, user_id):
        user = User(user_id=user_id, name="Alice")
        assert user.user_id == user_id
        assert user.name == "Alice"

    def test_init_empty_name_default(self, user_id):
        user = User(user_id=user_id)
        assert user.name == ""

    def test_get_children_empty_initially(self, user):
        assert user.get_children() == []

    def test_children_property_returns_iterable(self, user, child_data):
        """Property children возвращает итератор по детям (покрытие)."""
        assert list(user.children) == []
        user.add_child(child_data)
        assert len(list(user.children)) == 1

    def test_get_child_returns_none_for_unknown_id(self, user):
        assert user.get_child(uuid4()) is None


class TestUserAddChild:
    """User.add_child: успех, инвариант дубликата child_id."""

    def test_add_child_returns_child_with_data(self, user, child_data):
        child = user.add_child(child_data)
        assert child.child_id is not None
        assert child.name == "Kid"
        assert child.birthdate == date(2020, 5, 15)

    def test_add_child_appears_in_get_children(self, user, child_data):
        child = user.add_child(child_data)
        children = user.get_children()
        assert len(children) == 1
        assert children[0].child_id == child.child_id

    def test_get_child_returns_added_child(self, user, child_data):
        child = user.add_child(child_data)
        assert user.get_child(child.child_id) is child

    def test_add_child_with_explicit_child_id(self, user):
        cid = uuid4()
        data = ChildData(name="Named", birthdate=date(2019, 1, 1), child_id=cid)
        child = user.add_child(data)
        assert child.child_id == cid

    def test_add_child_duplicate_child_id_raises(self, user, child_data):
        user.add_child(child_data)
        data_same_id = ChildData(
            name="Other",
            birthdate=date(2021, 1, 1),
            child_id=user.get_children()[0].child_id,
        )
        with pytest.raises(ValueError, match="already exists"):
            user.add_child(data_same_id)


class TestUserArchiveChild:
    """User.archive_child/restore_child: soft-delete и восстановление."""

    def test_archive_child_hides_from_active_list(self, user, child_data):
        child = user.add_child(child_data)
        user.archive_child(child.child_id)
        assert user.get_child(child.child_id) is not None
        assert user.get_children() == []
        assert user.get_child(child.child_id).is_archived is True

    def test_archive_child_unknown_id_raises(self, user):
        with pytest.raises(ValueError, match="Child not found"):
            user.archive_child(uuid4())

    def test_archive_child_with_stories_allowed(self, user, child_data):
        child = user.add_child(child_data)
        child.add_story(StoryData(title="T", content="C"))
        user.archive_child(child.child_id)
        assert user.get_child(child.child_id).is_archived is True

    def test_restore_child_returns_to_active_list(self, user, child_data):
        child = user.add_child(child_data)
        user.archive_child(child.child_id)
        user.restore_child(child.child_id)
        assert user.get_child(child.child_id).is_archived is False
        assert len(user.get_children()) == 1


class TestUserUpdateChild:
    """User.update_child: name, birthdate, Child not found, неверный тип."""

    def test_update_child_name(self, user, child_data):
        child = user.add_child(child_data)
        user.update_child(child.child_id, name="Updated")
        assert user.get_child(child.child_id).name == "Updated"

    def test_update_child_birthdate(self, user, child_data):
        child = user.add_child(child_data)
        new_date = date(2021, 6, 20)
        user.update_child(child.child_id, birthdate=new_date)
        assert user.get_child(child.child_id).birthdate == new_date

    def test_update_child_both(self, user, child_data):
        child = user.add_child(child_data)
        user.update_child(child.child_id, name="New", birthdate=date(2022, 1, 1))
        c = user.get_child(child.child_id)
        assert c.name == "New"
        assert c.birthdate == date(2022, 1, 1)

    def test_update_child_partial_keeps_other_fields(self, user, child_data):
        child = user.add_child(child_data)
        user.update_child(child.child_id, name="OnlyName")
        c = user.get_child(child.child_id)
        assert c.name == "OnlyName"
        assert c.birthdate == date(2020, 5, 15)

    def test_update_child_unknown_id_raises(self, user):
        with pytest.raises(ValueError, match="Child not found"):
            user.update_child(uuid4(), name="X")

    def test_update_child_birthdate_not_date_raises(self, user, child_data):
        child = user.add_child(child_data)
        with pytest.raises(TypeError, match="date"):
            user.update_child(child.child_id, birthdate="2020-01-01")

    def test_update_child_name_not_str_raises(self, user, child_data):
        child = user.add_child(child_data)
        with pytest.raises(TypeError, match="name must be str"):
            user.update_child(child.child_id, name=123)

    def test_update_archived_child_raises(self, user, child_data):
        child = user.add_child(child_data)
        user.archive_child(child.child_id)
        with pytest.raises(ValueError, match="archived"):
            user.update_child(child.child_id, name="X")
