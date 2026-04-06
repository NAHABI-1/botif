# Architecture

## Overview
The platform separates pure trading logic from broker and UI concerns. Core business rules live in the engine and are consumed by the worker and API layers.

## Core Components
- Engine (`services/engine`): risk engine, strategies, backtesting, reconciliation domain services.
- Worker (`services/worker`): broker adapter, forward-testing harness, MT5 integration boundary.
- API (`services/api`): FastAPI backend, authentication, RBAC, operator controls.
- Database (`database`): SQLAlchemy models, Alembic migrations, repository layer.
- Dashboard (`dashboard`): React operator console.
- EA (`mql5`): MQL5 Expert Advisor that runs inside MT5 terminal.

## Data Flow
1. Strategy produces a signal.
2. Risk engine evaluates the signal and produces a trade decision.
3. Trade permission service emits risk/audit events.
4. Worker executes via broker adapter and reconciles broker state.
5. API exposes the persisted state for operators and the dashboard.

## Security Boundaries
- Risk engine is pure and has no broker dependency.
- MT5 adapter runs only on the Windows host with MT5 terminal.
- API and dashboard access is protected by RBAC and audit logging.

## State and Storage
- PostgreSQL stores risk events, trades, strategies, and audit logs.
- Alembic manages schema migrations.

## Deployment Topology
- MT5 terminal runs on a Windows VPS.
- Worker runs on the same Windows host as MT5.
- API + dashboard can run on Linux or Windows.
