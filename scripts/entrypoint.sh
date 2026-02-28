#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${APP_CMD:-}" ]]; then
  echo "APP_CMD is not set. Example: APP_CMD='python -m pytest -q'"
  exit 1
fi

exec ${APP_CMD}
