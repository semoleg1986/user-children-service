from __future__ import annotations

import os

_PERSISTENCE_INITIALIZED = False


def init_persistence() -> None:
    """
    Проверить готовность persistence слоя.

    При наличии DATABASE_URL проверяются зависимости SQLAlchemy.
    Применение миграций выполняется отдельно через Alembic.
    """
    global _PERSISTENCE_INITIALIZED
    if _PERSISTENCE_INITIALIZED:
        return

    if os.getenv("DATABASE_URL"):
        try:
            from src.infrastructure.persistence.sqlalchemy import get_session_factory
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "DATABASE_URL is set but SQLAlchemy dependencies are not installed. "
                "Run: make install"
            ) from exc

        if get_session_factory() is None:
            raise RuntimeError(
                "DATABASE_URL is set but SQLAlchemy session factory is not available"
            )

    _PERSISTENCE_INITIALIZED = True
