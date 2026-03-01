from uuid import UUID

from src.domain.aggregates.user import User


class Actor:
    """
    Контекст того, кто выполняет действие (Value-like объект).
    Передаётся из Application/Interface, не хранится в Domain.

    :param user_id: Идентификатор актёра.
    :type user_id: UUID
    :param is_admin: Флаг администратора.
    :type is_admin: bool
    """

    def __init__(self, user_id: UUID, is_admin: bool, org_id: str | None = None):
        self.user_id = user_id
        self.is_admin = is_admin
        self.org_id = org_id


class AccessPolicy:
    """
    Правила доступа к операциям над агрегатом User и его Child.
    Admin может действовать над любым User; User — только над собой.
    """

    @staticmethod
    def _can_act_on_user(actor: Actor, user: User) -> bool:
        """Actor может выполнять действия над данным User."""
        return actor.is_admin or actor.user_id == user.user_id

    @staticmethod
    def can_manage_user(actor: Actor, user_id: UUID) -> bool:
        """Может управлять пользователем (создание, деактивация)."""
        return actor.is_admin or actor.user_id == user_id

    @staticmethod
    def can_view_user(actor: Actor, user: User) -> bool:
        """Admin может просматривать любого User; User — себя."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_view_children(actor: Actor, user: User) -> bool:
        """Может просматривать детей пользователя. User — своих, Admin — любых."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_add_child(actor: Actor, user: User) -> bool:
        """Может добавить ребёнка данному User. User — только себе."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_remove_child(actor: Actor, user: User) -> bool:
        """Может удалить ребёнка у данного User."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_archive_child(actor: Actor, user: User) -> bool:
        """Может архивировать ребёнка у данного User."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_restore_child(actor: Actor, user: User) -> bool:
        """Может восстановить ребёнка у данного User."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_update_child(actor: Actor, user: User) -> bool:
        """Может изменить ребёнка у данного User."""
        return AccessPolicy._can_act_on_user(actor, user)

    @staticmethod
    def can_add_story(actor: Actor, user: User) -> bool:
        """Может добавить Story ребёнку данного User."""
        return AccessPolicy._can_act_on_user(actor, user)
