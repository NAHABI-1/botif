# API Specification (Summary)

Base path: `/api/v1`

## Auth
- `POST /auth/login`
- `POST /auth/logout`

## Health
- `GET /health`

## Trading
- `GET /positions`
- `GET /orders`
- `GET /executions`
- `GET /account-snapshots`

## Strategy
- `GET /strategy-runs`
- `GET /backtests`

## Governance
- `GET /risk-events`
- `GET /alerts`
- `GET /audit-logs`

## Operator Controls
- `POST /operator-controls/deployments/{deployment_id}/pause`
- `POST /operator-controls/deployments/{deployment_id}/resume`
- `POST /operator-controls/deployments/{deployment_id}/safe-mode`
- `POST /operator-controls/deployments/{deployment_id}/panic-stop`

All privileged routes require RBAC and emit audit logs.
