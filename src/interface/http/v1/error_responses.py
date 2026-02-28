from __future__ import annotations

from src.interface.http.problem_types import get_problem_type_base_url
from src.interface.http.v1.schemas import ProblemDetails

_BASE_URL = get_problem_type_base_url()

ADMIN_ERROR_RESPONSES = {
    401: {
        "model": ProblemDetails,
        "description": "Unauthorized",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/unauthorized",
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Authorization Bearer token is required",
                    "instance": "/v1/admin/users",
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
    403: {
        "model": ProblemDetails,
        "description": "Access denied",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/access-denied",
                    "title": "Access Denied",
                    "status": 403,
                    "detail": "Access denied",
                    "instance": "/v1/admin/users",
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
    404: {
        "model": ProblemDetails,
        "description": "Not found",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/not-found",
                    "title": "Not Found",
                    "status": 404,
                    "detail": "User not found",
                    "instance": (
                        "/v1/admin/users/123e4567-e89b-12d3-a456-426614174000/children"
                    ),
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
    409: {
        "model": ProblemDetails,
        "description": "Conflict",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/conflict",
                    "title": "Conflict",
                    "status": 409,
                    "detail": "User already exists",
                    "instance": "/v1/admin/users",
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
}


USER_ERROR_RESPONSES = {
    401: {
        "model": ProblemDetails,
        "description": "Unauthorized",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/unauthorized",
                    "title": "Unauthorized",
                    "status": 401,
                    "detail": "Authorization Bearer token is required",
                    "instance": "/v1/user/users",
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
    403: {
        "model": ProblemDetails,
        "description": "Access denied",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/access-denied",
                    "title": "Access Denied",
                    "status": 403,
                    "detail": "Access denied",
                    "instance": (
                        "/v1/user/users/123e4567-e89b-12d3-a456-426614174000/children"
                    ),
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
    404: {
        "model": ProblemDetails,
        "description": "Not found",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/not-found",
                    "title": "Not Found",
                    "status": 404,
                    "detail": "User not found",
                    "instance": (
                        "/v1/user/users/123e4567-e89b-12d3-a456-426614174000/children"
                    ),
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
    409: {
        "model": ProblemDetails,
        "description": "Conflict",
        "content": {
            "application/problem+json": {
                "example": {
                    "type": f"{_BASE_URL}/conflict",
                    "title": "Conflict",
                    "status": 409,
                    "detail": "Child with this id already exists",
                    "instance": (
                        "/v1/user/users/123e4567-e89b-12d3-a456-426614174000/children"
                    ),
                    "request_id": "4b1c5f8c-7f2b-4e7f-8f7a-6b76a0e3f6a1",
                }
            }
        },
    },
}
