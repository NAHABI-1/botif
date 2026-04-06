#!/usr/bin/env bash
set -euo pipefail

cd dashboard
npm ci
npm run build
exec npx serve -s dist -l "${MT5_DASHBOARD_PORT:-4173}"
