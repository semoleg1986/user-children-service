import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from dishka import make_async_container
from dishka.integrations.fastapi import FastapiProvider, setup_dishka
from fastapi import FastAPI, Request, Response

from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.infrastructure.clients.auth.settings import load_auth_settings
from src.interface.http.di import AppProvider
from src.interface.http.errors import (
    access_denied_handler,
    invariant_violation_handler,
    not_found_handler,
)
from src.interface.http.health import router as health_router
from src.interface.http.v1.admin.router import router as admin_router
from src.interface.http.v1.user.router import router as user_router
from src.interface.http.wiring import init_persistence

logger = logging.getLogger("user_children_service.http")


def create_app() -> FastAPI:
    container = make_async_container(AppProvider(), FastapiProvider())

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        yield
        await container.close()

    # Fail fast on misconfiguration at startup
    load_auth_settings()
    init_persistence()

    app = FastAPI(title="Child Management Service", lifespan=lifespan)

    @app.middleware("http")
    async def correlation_id_middleware(request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid4())
        request.state.request_id = request_id
        response: Response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        logger.info(
            "request",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        return response

    app.add_exception_handler(NotFoundError, not_found_handler)
    app.add_exception_handler(AccessDeniedError, access_denied_handler)
    app.add_exception_handler(InvariantViolationError, invariant_violation_handler)

    app.include_router(health_router, tags=["health"])
    app.include_router(admin_router, prefix="/v1/admin", tags=["admin"])
    app.include_router(user_router, prefix="/v1/user", tags=["user"])

    setup_dishka(container=container, app=app)

    return app
