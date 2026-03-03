from __future__ import annotations

import os
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .models import Base


def _normalize_database_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return "postgresql+asyncpg://" + url.removeprefix("postgresql://")
    return url


def get_database_url() -> str | None:
    return os.getenv("DATABASE_URL")


def is_database_enabled() -> bool:
    return bool(get_database_url())


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine | None:
    raw_url = get_database_url()
    if not raw_url:
        return None
    return create_async_engine(_normalize_database_url(raw_url), pool_pre_ping=True)


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession] | None:
    engine = get_engine()
    if engine is None:
        return None
    return async_sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


async def ensure_schema() -> None:
    engine = get_engine()
    if engine is None:
        return
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
