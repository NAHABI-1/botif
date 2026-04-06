from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from enum import Enum

from mt5_platform_engine.risk.enums import HaltState, TradeSide
from mt5_platform_engine.strategy.models import StrategySignal
from mt5_platform_engine.trading.models import AuditLogRecord, RiskViolationEvent, TradePermissionDecision


class ForwardExecutionMode(str, Enum):
    PAPER = "paper"
    DEMO = "demo"


@dataclass(frozen=True, slots=True)
class ForwardSessionConfig:
    session_name: str
    symbol: str
    timeframe: str
    mode: ForwardExecutionMode = ForwardExecutionMode.PAPER
    starting_cash: Decimal = Decimal("10000")
    allow_demo_execution: bool = False


@dataclass(frozen=True, slots=True)
class ForwardExecutionRecord:
    mode: ForwardExecutionMode
    signal_action: str
    attempted: bool
    success: bool
    requested_side: TradeSide
    requested_quantity: Decimal
    requested_price: Decimal | None
    occurred_at: datetime
    synthetic: bool


@dataclass(frozen=True, slots=True)
class ForwardCycleResult:
    observed_at: datetime
    signal: StrategySignal
    permission_decision: TradePermissionDecision | None
    execution: ForwardExecutionRecord | None
    halt_state: HaltState = HaltState.ACTIVE
    risk_events: tuple[RiskViolationEvent, ...] = ()
    audit_entries: tuple[AuditLogRecord, ...] = ()


@dataclass(frozen=True, slots=True)
class ForwardTestReport:
    config: ForwardSessionConfig
    cycles: tuple[ForwardCycleResult, ...]
