#!/usr/bin/env bash
set -euo pipefail

if [[ -z "${MT5_DB_URL:-}" ]]; then
  echo "MT5_DB_URL is required."
  exit 1
fi

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP="$(date -u +%Y%m%d_%H%M%S)"
mkdir -p "${BACKUP_DIR}"
pg_dump "${MT5_DB_URL}" | gzip > "${BACKUP_DIR}/mt5_platform_${TIMESTAMP}.sql.gz"
