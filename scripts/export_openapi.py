#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path


def _ensure_env() -> None:
    os.environ.setdefault("AUTH_JWKS_URL", "http://jwks.local")
    os.environ.setdefault("AUTH_ISSUER", "auth-service")
    os.environ.setdefault("AUTH_AUDIENCE", "user-children-service")
    os.environ.setdefault("AUTH_ALGORITHMS", "RS256")


def _render_openapi() -> str:
    _ensure_env()
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    from src.interface.http.app import create_app

    app = create_app()
    spec = app.openapi()
    return json.dumps(spec, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Export OpenAPI spec as a versioned artifact."
    )
    parser.add_argument(
        "--output",
        default="openapi.yaml",
        help="Output file path (default: openapi.yaml)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if current openapi file differs from generated spec.",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    rendered = _render_openapi()

    if args.check:
        if not output_path.exists():
            print(f"[contract] Missing file: {output_path}")
            return 1
        current = output_path.read_text(encoding="utf-8")
        if current != rendered:
            print(
                f"[contract] OpenAPI artifact is out of date: {output_path}. "
                "Run: make openapi-export"
            )
            return 1
        print(f"[contract] OpenAPI artifact is up to date: {output_path}")
        return 0

    output_path.write_text(rendered, encoding="utf-8")
    print(f"[contract] OpenAPI exported to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
