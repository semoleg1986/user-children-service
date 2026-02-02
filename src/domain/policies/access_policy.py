from uuid import UUID


class Actor:
    """
    Контекст того, кто выполняет действие.
    Это НЕ Entity, а Value-like объект.
    """

    def __init__(self, user_id: UUID, is_admin: bool):
        self.user_id = user_id
        self.is_admin = is_admin


class AccessPolicy:

    @staticmethod
    def can_manage_user(actor: Actor, user_id: UUID) -> bool:
        return actor.is_admin or actor.user_id == user_id