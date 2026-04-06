#!/usr/bin/env bash
set -euo pipefail

export PYTHONUNBUFFERED=1
export PYTHONDONTWRITEBYTECODE=1

exec uvicorn mt5_platform_api.app:app --host 0.0.0.0 --port "${MT5_API_PORT:-8000}"
