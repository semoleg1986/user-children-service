from __future__ import annotations

from fastapi import Request
from starlette.responses import JSONResponse

from src.application.errors import (
    AccessDeniedError,
    InvariantViolationError,
    NotFoundError,
)
from src.interface.http.problem_types import get_problem_type_base_url


def problem_response(
    *,
    status_code: int,
    title: str,
    detail: str,
    type_suffix: str,
    request: Request,
) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    base_url = get_problem_type_base_url()
    return JSONResponse(
        status_code=status_code,
        media_type="application/problem+json",
        content={
            "type": f"{base_url}/{type_suffix}",
            "title": title,
            "status": status_code,
            "detail": detail,
            "instance": request.url.path,
            "request_id": request_id,
        },
    )


def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
    return problem_response(
        status_code=404,
        title="Not Found",
        detail=str(exc),
        type_suffix="not-found",
        request=request,
    )


def access_denied_handler(request: Request, exc: AccessDeniedError) -> JSONResponse:
    return problem_response(
        status_code=403,
        title="Access Denied",
        detail=str(exc),
        type_suffix="access-denied",
        request=request,
    )


def invariant_violation_handler(
    request: Request, exc: InvariantViolationError
) -> JSONResponse:
    return problem_response(
        status_code=409,
        title="Conflict",
        detail=str(exc),
        type_suffix="conflict",
        request=request,
    )
