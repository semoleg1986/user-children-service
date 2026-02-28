"""Unit-тесты политик доступа AccessPolicy и Actor."""

from uuid import uuid4

import pytest

from src.domain.aggregates.user import User
from src.domain.policies import AccessPolicy, Actor


@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def other_user_id():
    return uuid4()


@pytest.fixture
def user(user_id):
    return User(user_id=user_id, name="Owner")


@pytest.fixture
def other_user(other_user_id):
    return User(user_id=other_user_id, name="Other")


@pytest.fixture
def actor_user(user_id):
    """Обычный пользователь (не Admin)."""
    return Actor(user_id=user_id, is_admin=False)


@pytest.fixture
def actor_admin(user_id):
    """Админ (может действовать над любым User)."""
    return Actor(user_id=user_id, is_admin=True)


class TestCanManageUser:
    """can_manage_user(actor, user_id): по user_id без загрузки User."""

    def test_user_can_manage_self(self, actor_user, user_id):
        assert AccessPolicy.can_manage_user(actor_user, user_id) is True

    def test_user_cannot_manage_other(self, actor_user, other_user_id):
        assert AccessPolicy.can_manage_user(actor_user, other_user_id) is False

    def test_admin_can_manage_any(self, actor_admin, other_user_id):
        assert AccessPolicy.can_manage_user(actor_admin, other_user_id) is True


class TestCanViewUser:
    """can_view_user(actor, user)."""

    def test_user_can_view_self(self, actor_user, user):
        assert AccessPolicy.can_view_user(actor_user, user) is True

    def test_user_cannot_view_other(self, actor_user, other_user):
        assert AccessPolicy.can_view_user(actor_user, other_user) is False

    def test_admin_can_view_any(self, actor_admin, other_user):
        assert AccessPolicy.can_view_user(actor_admin, other_user) is True


class TestCanViewChildren:
    """can_view_children(actor, user)."""

    def test_user_can_view_own_children(self, actor_user, user):
        assert AccessPolicy.can_view_children(actor_user, user) is True

    def test_user_cannot_view_other_children(self, actor_user, other_user):
        assert AccessPolicy.can_view_children(actor_user, other_user) is False

    def test_admin_can_view_any_children(self, actor_admin, other_user):
        assert AccessPolicy.can_view_children(actor_admin, other_user) is True


class TestCanAddChild:
    """can_add_child(actor, user)."""

    def test_user_can_add_to_self(self, actor_user, user):
        assert AccessPolicy.can_add_child(actor_user, user) is True

    def test_user_cannot_add_to_other(self, actor_user, other_user):
        assert AccessPolicy.can_add_child(actor_user, other_user) is False

    def test_admin_can_add_to_any(self, actor_admin, other_user):
        assert AccessPolicy.can_add_child(actor_admin, other_user) is True


class TestCanRemoveChild:
    """can_remove_child(actor, user)."""

    def test_user_can_remove_own(self, actor_user, user):
        assert AccessPolicy.can_remove_child(actor_user, user) is True

    def test_user_cannot_remove_other(self, actor_user, other_user):
        assert AccessPolicy.can_remove_child(actor_user, other_user) is False

    def test_admin_can_remove_any(self, actor_admin, other_user):
        assert AccessPolicy.can_remove_child(actor_admin, other_user) is True


class TestCanArchiveRestoreChild:
    """can_archive_child/can_restore_child(actor, user)."""

    def test_user_can_archive_own(self, actor_user, user):
        assert AccessPolicy.can_archive_child(actor_user, user) is True

    def test_user_cannot_archive_other(self, actor_user, other_user):
        assert AccessPolicy.can_archive_child(actor_user, other_user) is False

    def test_admin_can_archive_any(self, actor_admin, other_user):
        assert AccessPolicy.can_archive_child(actor_admin, other_user) is True

    def test_user_can_restore_own(self, actor_user, user):
        assert AccessPolicy.can_restore_child(actor_user, user) is True

    def test_user_cannot_restore_other(self, actor_user, other_user):
        assert AccessPolicy.can_restore_child(actor_user, other_user) is False

    def test_admin_can_restore_any(self, actor_admin, other_user):
        assert AccessPolicy.can_restore_child(actor_admin, other_user) is True


class TestCanUpdateChild:
    """can_update_child(actor, user)."""

    def test_user_can_update_own(self, actor_user, user):
        assert AccessPolicy.can_update_child(actor_user, user) is True

    def test_user_cannot_update_other(self, actor_user, other_user):
        assert AccessPolicy.can_update_child(actor_user, other_user) is False

    def test_admin_can_update_any(self, actor_admin, other_user):
        assert AccessPolicy.can_update_child(actor_admin, other_user) is True


class TestCanAddStory:
    """can_add_story(actor, user)."""

    def test_user_can_add_story_to_own_child(self, actor_user, user):
        assert AccessPolicy.can_add_story(actor_user, user) is True

    def test_user_cannot_add_story_to_other(self, actor_user, other_user):
        assert AccessPolicy.can_add_story(actor_user, other_user) is False

    def test_admin_can_add_story_to_any(self, actor_admin, other_user):
        assert AccessPolicy.can_add_story(actor_admin, other_user) is True
