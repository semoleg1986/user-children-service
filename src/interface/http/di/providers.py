from __future__ import annotations

import os
from typing import AsyncIterator

from dishka import Provider, Scope, provide
from fastapi import HTTPException
from starlette import status
from starlette.requests import Request

from src.application.auth import AuthService
from src.application.unit_of_work import (
    AsyncAuditRepository,
    AsyncUserRepository,
    UnitOfWork,
)
from src.domain.policies.access_policy import Actor
from src.infrastructure.clients.auth.jwks_cache import JWKSCache
from src.infrastructure.clients.auth.jwt_auth_service import JwtAuthService
from src.infrastructure.clients.auth.settings import AuthSettings, load_auth_settings
from src.infrastructure.persistence.repositories.in_memory_audit_repository import (
    InMemoryAuditRepository,
)
from src.infrastructure.persistence.repositories.in_memory_user_repository import (
    InMemoryUserRepository,
)
from src.infrastructure.persistence.uow.in_memory_uow import InMemoryUnitOfWork


class AppProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_auth_settings(self) -> AuthSettings:
        return load_auth_settings()

    @provide(scope=Scope.APP)
    def provide_jwks_cache(self, settings: AuthSettings) -> JWKSCache:
        return JWKSCache(settings.jwks_url, ttl_seconds=settings.jwks_cache_ttl_seconds)

    @provide(scope=Scope.APP)
    def provide_auth_service(
        self, settings: AuthSettings, jwks_cache: JWKSCache
    ) -> AuthService:
        return JwtAuthService(settings=settings, jwks_cache=jwks_cache)

    @provide(scope=Scope.APP)
    def provide_repo(self) -> AsyncUserRepository:
        return InMemoryUserRepository()

    @provide(scope=Scope.APP)
    def provide_audit_repo(self) -> AsyncAuditRepository:
        return InMemoryAuditRepository()

    @provide(scope=Scope.REQUEST)
    async def provide_uow(
        self, repo: AsyncUserRepository, audit_repo: AsyncAuditRepository
    ) -> AsyncIterator[UnitOfWork]:
        if os.getenv("DATABASE_URL"):
            from src.infrastructure.persistence.sqlalchemy import get_session_factory
            from src.infrastructure.persistence.uow.sqlalchemy_uow import (
                SqlAlchemyUnitOfWork,
            )

            session_factory = get_session_factory()
            if session_factory is None:
                raise RuntimeError(
                    (
                        "DATABASE_URL is set but SQLAlchemy session factory "
                        "is not available"
                    )
                )
            session = session_factory()
            uow = SqlAlchemyUnitOfWork(session)
            try:
                yield uow
            except Exception:
                await uow.rollback()
                raise
            finally:
                await uow.close()
            return

        yield InMemoryUnitOfWork(user_repo=repo, audit_repo=audit_repo)

    @provide(scope=Scope.REQUEST)
    async def provide_actor(self, request: Request, auth_service: AuthService) -> Actor:
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization Bearer token is required",
            )
        token = auth_header.removeprefix("Bearer ").strip()
        try:
            return await auth_service.authenticate(token)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            ) from exc
