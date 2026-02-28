from __future__ import annotations

import os

_DEFAULT_PROBLEM_TYPE_BASE_URL = "https://example.com/problems"


def get_problem_type_base_url() -> str:
    base_url = os.getenv(
        "PROBLEM_TYPE_BASE_URL", _DEFAULT_PROBLEM_TYPE_BASE_URL
    ).strip()
    if not base_url:
        return _DEFAULT_PROBLEM_TYPE_BASE_URL
    return base_url.rstrip("/")
