from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
import uuid

from mt5_platform_engine.risk.enums import HaltState, TradeSide
from mt5_platform_engine.risk.models import EmergencyFlags, InstrumentRiskProfile, MarketSnapshot, PortfolioRiskSnapshot, RiskEvaluation, TradeIntent
from mt5_platform_engine.trading.enums import DomainAuditActorType, DomainRiskCategory, DomainRiskSeverity, ReconciliationStatus


@dataclass(frozen=True, slots=True)
class ServiceContext:
    deployment_id: uuid.UUID | None = None
    strategy_config_id: uuid.UUID | None = None
    strategy_run_id: uuid.UUID | None = None
    signal_event_id: uuid.UUID | None = None
    order_request_id: uuid.UUID | None = None
    order_result_id: uuid.UUID | None = None
    actor_user_id: uuid.UUID | None = None
    actor_type: DomainAuditActorType = DomainAuditActorType.SERVICE
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class TradingControlState:
    halt_state: HaltState = HaltState.ACTIVE
    reasons: tuple[str, ...] = ()
    updated_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class HaltStatusResult:
    halt_state: HaltState
    is_halted: bool
    allow_new_trades: bool
    safe_mode_active: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EscalationDecision:
    target_halt_state: HaltState
    safe_mode_requested: bool
    panic_stop_requested: bool
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RiskViolationEvent:
    severity: DomainRiskSeverity
    category: DomainRiskCategory
    code: str
    message: str
    details: dict[str, object]
    occurred_at: datetime
    deployment_id: uuid.UUID | None = None
    strategy_config_id: uuid.UUID | None = None
    strategy_run_id: uuid.UUID | None = None
    signal_event_id: uuid.UUID | None = None
    order_request_id: uuid.UUID | None = None
    order_result_id: uuid.UUID | None = None


@dataclass(frozen=True, slots=True)
class AuditLogRecord:
    action: str
    actor_type: DomainAuditActorType
    occurred_at: datetime
    changes: dict[str, object]
    audit_metadata: dict[str, object]
    actor_user_id: uuid.UUID | None = None
    deployment_id: uuid.UUID | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class TradePermissionRequest:
    context: ServiceContext
    intent: TradeIntent
    portfolio: PortfolioRiskSnapshot
    instrument: InstrumentRiskProfile
    market: MarketSnapshot | None = None
    emergency_flags: EmergencyFlags | None = None
    control_state: TradingControlState | None = None


@dataclass(frozen=True, slots=True)
class TradePermissionDecision:
    allowed: bool
    halt_status: HaltStatusResult
    escalation: EscalationDecision
    reasons: tuple[str, ...] = ()
    risk_evaluation: RiskEvaluation | None = None
    violation_events: tuple[RiskViolationEvent, ...] = ()
    audit_entries: tuple[AuditLogRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class BrokerOrderState:
    broker_order_id: str
    symbol: str
    side: TradeSide
    quantity: Decimal
    status: str
    limit_price: Decimal | None = None


@dataclass(frozen=True, slots=True)
class BrokerPositionState:
    broker_position_id: str
    symbol: str
    side: TradeSide
    quantity: Decimal
    average_price: Decimal


@dataclass(frozen=True, slots=True)
class BrokerAccountState:
    balance: Decimal
    equity: Decimal
    margin: Decimal
    free_margin: Decimal


@dataclass(frozen=True, slots=True)
class BrokerReportedState:
    observed_at: datetime
    orders: tuple[BrokerOrderState, ...] = ()
    positions: tuple[BrokerPositionState, ...] = ()
    account: BrokerAccountState | None = None


@dataclass(frozen=True, slots=True)
class InternalOrderState:
    internal_order_id: str
    broker_order_id: str
    symbol: str
    side: TradeSide
    quantity: Decimal
    status: str
    limit_price: Decimal | None = None


@dataclass(frozen=True, slots=True)
class InternalPositionState:
    internal_position_id: str
    broker_position_id: str
    symbol: str
    side: TradeSide
    quantity: Decimal
    average_price: Decimal


@dataclass(frozen=True, slots=True)
class ExpectedAccountState:
    balance: Decimal
    equity: Decimal
    margin: Decimal
    free_margin: Decimal


@dataclass(frozen=True, slots=True)
class ExpectedTradingState:
    orders: tuple[InternalOrderState, ...] = ()
    positions: tuple[InternalPositionState, ...] = ()
    account: ExpectedAccountState | None = None


@dataclass(frozen=True, slots=True)
class ReconciliationViolation:
    code: str
    message: str
    details: dict[str, object]


@dataclass(frozen=True, slots=True)
class ReconciliationResult:
    status: ReconciliationStatus
    in_sync: bool
    violations: tuple[ReconciliationViolation, ...]
    escalation: EscalationDecision
    matched_order_ids: tuple[str, ...] = ()
    matched_position_ids: tuple[str, ...] = ()
    violation_events: tuple[RiskViolationEvent, ...] = ()
    audit_entries: tuple[AuditLogRecord, ...] = ()
