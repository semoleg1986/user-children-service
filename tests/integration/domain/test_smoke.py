"""
Интеграционный (smoke) тест: Domain + FakeUserRepository.
Проверяет сценарий как из Application Layer: репозиторий → Policy → агрегат → save.
"""

from datetime import date
from uuid import uuid4

from src.domain.aggregates.user import User
from src.domain.policies import AccessPolicy, Actor
from src.domain.value_objects import ChildData, StoryData
from tests.integration.domain.fake_user_repository import FakeUserRepository


class TestSmokeApplicationFlow:
    """
    Smoke: полный сценарий без реальной БД.
    Порядок шагов как в 06-application-layer (без UnitOfWork и is_authenticated).
    """

    def test_add_child_view_children_update_archive_restore_full_flow(self) -> None:
        """Создать пользователя, add child, view, updated, archived, recovery."""
        repo = FakeUserRepository()
        user_id = uuid4()
        user = User(user_id=user_id, name="Alice")
        repo.save(user)

        # "Get User"
        loaded = repo.get_by_id(user_id)
        assert loaded is not None
        assert loaded.user_id == user_id
        assert loaded.get_children() == []

        # Add Child (as owner)
        actor = Actor(user_id=user_id, is_admin=False)
        assert AccessPolicy.can_add_child(actor, loaded) is True
        child_data = ChildData(name="Kid", birthdate=date(2020, 5, 15))
        child = loaded.add_child(child_data)
        repo.save(loaded)

        # View Children
        loaded2 = repo.get_by_id(user_id)
        assert loaded2 is not None
        children = loaded2.get_children()
        assert len(children) == 1
        assert children[0].name == "Kid"
        assert children[0].child_id == child.child_id

        # Update Child
        assert AccessPolicy.can_update_child(actor, loaded2) is True
        loaded2.update_child(child.child_id, name="Updated Kid")
        repo.save(loaded2)

        loaded3 = repo.get_by_id(user_id)
        assert loaded3 is not None
        c = loaded3.get_child(child.child_id)
        assert c is not None
        assert c.name == "Updated Kid"

        # Archive Child (soft-delete)
        assert AccessPolicy.can_archive_child(actor, loaded3) is True
        loaded3.archive_child(child.child_id)
        repo.save(loaded3)

        loaded4 = repo.get_by_id(user_id)
        assert loaded4 is not None
        assert loaded4.get_children() == []
        assert loaded4.get_child(child.child_id) is not None
        assert loaded4.get_child(child.child_id).is_archived is True

        # Restore Child
        assert AccessPolicy.can_restore_child(actor, loaded4) is True
        loaded4.restore_child(child.child_id)
        repo.save(loaded4)
        loaded5 = repo.get_by_id(user_id)
        assert loaded5 is not None
        assert len(loaded5.get_children()) == 1

    def test_add_story_then_archive_child_allowed(self) -> None:
        """Добавить историю ребёнку; архивирование с историями допустимо."""
        repo = FakeUserRepository()
        user_id = uuid4()
        user = User(user_id=user_id, name="Bob")
        repo.save(user)

        loaded = repo.get_by_id(user_id)
        assert loaded is not None
        child = loaded.add_child(ChildData(name="Kid", birthdate=date(2019, 1, 1)))
        loaded.get_child(child.child_id).add_story(StoryData(title="T", content="C"))
        repo.save(loaded)

        loaded2 = repo.get_by_id(user_id)
        assert loaded2 is not None
        actor = Actor(user_id=user_id, is_admin=False)
        assert AccessPolicy.can_archive_child(actor, loaded2) is True
        loaded2.archive_child(child.child_id)
        assert loaded2.get_child(child.child_id) is not None
        assert loaded2.get_child(child.child_id).is_archived is True

    def test_admin_can_act_on_other_user_children(self) -> None:
        """Admin добавляет ребёнка другому пользователю через репозиторий."""
        repo = FakeUserRepository()
        owner_id = uuid4()
        admin_id = uuid4()
        user = User(user_id=owner_id, name="Owner")
        repo.save(user)

        loaded = repo.get_by_id(owner_id)
        assert loaded is not None
        actor_admin = Actor(user_id=admin_id, is_admin=True)
        assert AccessPolicy.can_add_child(actor_admin, loaded) is True
        loaded.add_child(ChildData(name="Admin Added", birthdate=date(2021, 1, 1)))
        repo.save(loaded)

        loaded2 = repo.get_by_id(owner_id)
        assert loaded2 is not None
        children = loaded2.get_children()
        assert len(children) == 1
        assert children[0].name == "Admin Added"

    def test_user_cannot_add_child_to_other_user_rejected_by_policy(self) -> None:
        """Обычный пользователь не может добавить ребёнка чужому User."""
        repo = FakeUserRepository()
        owner_id = uuid4()
        other_id = uuid4()
        user = User(user_id=owner_id, name="Owner")
        repo.save(user)

        loaded = repo.get_by_id(owner_id)
        assert loaded is not None
        actor_other = Actor(user_id=other_id, is_admin=False)
        assert AccessPolicy.can_add_child(actor_other, loaded) is False
        # В реальном Use Case здесь был бы raise AccessDeniedError;
        # в тесте только проверяем Policy
        # Не вызываем loaded.add_child — доступ уже запрещён

    def test_get_by_id_returns_none_for_missing_user(self) -> None:
        """Репозиторий возвращает None для неизвестного user_id."""
        repo = FakeUserRepository()
        assert repo.get_by_id(uuid4()) is None

    def test_delete_user_removes_from_repo(self) -> None:
        """delete(user_id) удаляет пользователя из репозитория."""
        repo = FakeUserRepository()
        user_id = uuid4()
        repo.save(User(user_id=user_id, name="X"))
        assert repo.get_by_id(user_id) is not None
        repo.delete(user_id)
        assert repo.get_by_id(user_id) is None
