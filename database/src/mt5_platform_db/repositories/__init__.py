from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from mt5_platform_db.repositories.governance import AlertRepository, AuditLogRepository, RiskEventRepository
from mt5_platform_db.repositories.identity import RoleRepository, SessionRepository, UserRepository
from mt5_platform_db.repositories.strategy import DeploymentRepository, StrategyConfigRepository, StrategyRunRepository
from mt5_platform_db.repositories.trading import (
    AccountSnapshotRepository,
    ExecutionRepository,
    OrderRequestRepository,
    OrderResultRepository,
    PositionSnapshotRepository,
    SignalEventRepository,
)


@dataclass(slots=True)
class RepositoryContainer:
    users: UserRepository
    roles: RoleRepository
    sessions: SessionRepository
    strategy_configs: StrategyConfigRepository
    deployments: DeploymentRepository
    strategy_runs: StrategyRunRepository
    signal_events: SignalEventRepository
    order_requests: OrderRequestRepository
    order_results: OrderResultRepository
    executions: ExecutionRepository
    positions: PositionSnapshotRepository
    account_snapshots: AccountSnapshotRepository
    risk_events: RiskEventRepository
    alerts: AlertRepository
    audit_logs: AuditLogRepository


def build_repositories(session: Session) -> RepositoryContainer:
    return RepositoryContainer(
        users=UserRepository(session),
        roles=RoleRepository(session),
        sessions=SessionRepository(session),
        strategy_configs=StrategyConfigRepository(session),
        deployments=DeploymentRepository(session),
        strategy_runs=StrategyRunRepository(session),
        signal_events=SignalEventRepository(session),
        order_requests=OrderRequestRepository(session),
        order_results=OrderResultRepository(session),
        executions=ExecutionRepository(session),
        positions=PositionSnapshotRepository(session),
        account_snapshots=AccountSnapshotRepository(session),
        risk_events=RiskEventRepository(session),
        alerts=AlertRepository(session),
        audit_logs=AuditLogRepository(session),
    )
