from __future__ import annotations

from src.interface.http.app import create_app


def test_openapi_contains_versioned_admin_audit_endpoint() -> None:
    spec = create_app().openapi()
    path = spec["paths"]["/v1/admin/audit/events"]["get"]

    assert path["responses"]["200"]["content"]["application/json"]["schema"][
        "type"
    ] == ("array")
    assert "401" in path["responses"]
    assert "403" in path["responses"]


def test_openapi_problem_json_contract_present() -> None:
    spec = create_app().openapi()
    path = spec["paths"]["/v1/user/users/{user_id}/children"]["post"]
    conflict = path["responses"]["409"]

    assert "application/problem+json" in conflict["content"]
    example = conflict["content"]["application/problem+json"]["example"]
    assert example["status"] == 409
    assert example["title"] == "Conflict"
