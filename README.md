# MT5 Automated Trading Platform

Production-grade MetaTrader 5 automated trading platform with clean architecture, risk-first controls, broker-agnostic core, and operator-focused tooling.

## Project Overview
- Risk engine with explicit guards, safe mode, and panic stop flows.
- Strategy engine with deterministic, parameterized strategies.
- Backtesting and forward-testing harnesses.
- MT5 broker adapter and Expert Advisor skeleton.
- FastAPI backend with RBAC and audit logging.
- React dashboard for operators.

## Architecture Summary
- Core engine: risk, strategy, backtesting, and reconciliation logic (`services/engine`).
- Broker adapter and forward testing (`services/worker`), MT5 terminal runs on Windows host.
- API (`services/api`) for operators and dashboards.
- Database (`database`) with Alembic migrations and repository layer.
- MQL5 EA (`mql5`) runs inside the MT5 terminal.

See detailed docs:
- `docs/architecture.md`
- `docs/deployment.md`
- `docs/runbook.md`

## Prerequisites
- Python 3.11+
- Node.js 20+ (dashboard)
- Docker (for Postgres/support services)
- Windows VPS (for MT5 terminal and broker adapter)

## Local Setup
1. Start support services:
```bash
docker compose -f infra/docker-compose.support.yml up -d
```
2. Install Python deps:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e database -e services/engine -e services/worker -e services/api
```
3. Run migrations:
```bash
alembic -c database/alembic.ini upgrade head
```
4. Start API:
```bash
./scripts/start_api.sh
```
5. Start dashboard:
```bash
./scripts/start_dashboard.sh
```

## Testing Steps
```bash
pytest
```

## Backtesting Steps
```bash
python -c "from mt5_platform_engine.backtesting import BacktestRunner; print('backtesting ready')"
```
See `docs/MT5_BACKTESTING.md` for full usage examples.

## Demo-Trading Steps
1. Install MT5 terminal on the Windows host.
2. Place EA files as described in `docs/MT5_TERMINAL_SETUP.md`.
3. Run the worker on the same Windows host as MT5.
4. Use demo credentials only until explicitly approved for live trading.

## Dashboard Usage
- Start dashboard with `./scripts/start_dashboard.sh`.
- Login using seeded demo users (see database seed scripts).
- Navigate to Overview, Positions, Orders, Risk, Backtests, Alerts.

## Operator Controls
- Pause trading
- Resume trading
- Enable safe mode
- Trigger panic stop

See `docs/runbook.md` for detailed procedures.

## Production Warnings
- Live trading is disabled by default.
- Do not enable MT5 live execution without documented approval and a rollback plan.

## Live Trading Caution
Trading involves substantial risk. This platform provides safety controls but does not guarantee profit or loss avoidance. Always run in demo or paper mode first.
