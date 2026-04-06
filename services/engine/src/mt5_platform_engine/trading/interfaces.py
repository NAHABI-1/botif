from __future__ import annotations

from typing import Protocol

from mt5_platform_engine.trading.models import AuditLogRecord, BrokerReportedState, RiskViolationEvent, TradingControlState


class RiskEventSink(Protocol):
    def publish_risk_event(self, event: RiskViolationEvent) -> None:
        ...


class AuditLogSink(Protocol):
    def publish_audit_log(self, record: AuditLogRecord) -> None:
        ...


class BrokerStateProvider(Protocol):
    def get_broker_reported_state(self) -> BrokerReportedState:
        ...


class TradingControlStateProvider(Protocol):
    def get_trading_control_state(self) -> TradingControlState:
        ...
