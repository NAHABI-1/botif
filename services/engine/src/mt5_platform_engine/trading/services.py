from __future__ import annotations

from dataclasses import replace

from mt5_platform_engine.risk.engine import RiskEngine
from mt5_platform_engine.risk.enums import HaltState
from mt5_platform_engine.risk.models import RiskEvaluation
from mt5_platform_engine.trading.interfaces import AuditLogSink, BrokerStateProvider, RiskEventSink, TradingControlStateProvider
from mt5_platform_engine.trading.models import (
    AuditLogRecord,
    BrokerReportedState,
    EscalationDecision,
    ExpectedTradingState,
    HaltStatusResult,
    ReconciliationResult,
    ReconciliationStatus,
    ReconciliationViolation,
    ServiceContext,
    TradePermissionDecision,
    TradePermissionRequest,
    TradingControlState,
)
from mt5_platform_engine.trading.enums import DomainRiskCategory, DomainRiskSeverity


class TradingHaltQueryService:
    def __init__(self, provider: TradingControlStateProvider | None = None) -> None:
        self._provider = provider

    def get_status(self, state: TradingControlState | None = None) -> HaltStatusResult:
        resolved = state or self._load_state()
        halt_state = resolved.halt_state
        is_halted = halt_state in {HaltState.HALTED, HaltState.PANIC_STOP}
        return HaltStatusResult(
            halt_state=halt_state,
            is_halted=is_halted,
            allow_new_trades=not is_halted,
            safe_mode_active=halt_state == HaltState.SAFE_MODE,
            reasons=resolved.reasons,
        )

    def _load_state(self) -> TradingControlState:
        if self._provider is None:
            return TradingControlState()
        return self._provider.get_trading_control_state()


class TradePermissionService:
    def __init__(
        self,
        *,
        risk_engine: RiskEngine,
        halt_service: TradingHaltQueryService | None = None,
        risk_event_sink: RiskEventSink | None = None,
        audit_log_sink: AuditLogSink | None = None,
    ) -> None:
        self._risk_engine = risk_engine
        self._halt_service = halt_service or TradingHaltQueryService()
        self._risk_event_sink = risk_event_sink
        self._audit_log_sink = audit_log_sink

    def determine_if_new_trade_is_allowed(self, request: TradePermissionRequest) -> TradePermissionDecision:
        halt_status = self._halt_service.get_status(request.control_state)
        if halt_status.is_halted:
            escalation = self._escalation_for_halt_state(halt_status)
            return TradePermissionDecision(
                allowed=False,
                halt_status=halt_status,
                escalation=escalation,
                reasons=halt_status.reasons,
            )

        portfolio = request.portfolio
        if request.control_state is not None and portfolio.halt_state != request.control_state.halt_state:
            portfolio = replace(portfolio, halt_state=request.control_state.halt_state)

        risk_evaluation = self._risk_engine.evaluate(
            intent=request.intent,
            portfolio=portfolio,
            instrument=request.instrument,
            market=request.market,
            emergency_flags=request.emergency_flags,
        )
        escalation = self._escalation_from_risk_evaluation(risk_evaluation)
        decision = TradePermissionDecision(
            allowed=risk_evaluation.allowed,
            halt_status=halt_status,
            escalation=escalation,
            reasons=risk_evaluation.reasons,
            risk_evaluation=risk_evaluation,
        )
        return decision

    @staticmethod
    def _escalation_for_halt_state(halt_status: HaltStatusResult) -> EscalationDecision:
        return EscalationDecision(
            target_halt_state=halt_status.halt_state,
            safe_mode_requested=halt_status.halt_state == HaltState.SAFE_MODE,
            panic_stop_requested=halt_status.halt_state == HaltState.PANIC_STOP,
            reasons=halt_status.reasons,
        )

    @staticmethod
    def _escalation_from_risk_evaluation(risk_evaluation: RiskEvaluation) -> EscalationDecision:
        return EscalationDecision(
            target_halt_state=risk_evaluation.halt_state,
            safe_mode_requested=risk_evaluation.halt_state == HaltState.SAFE_MODE,
            panic_stop_requested=risk_evaluation.halt_state == HaltState.PANIC_STOP,
            reasons=risk_evaluation.reasons,
        )


class TradingReconciliationService:
    def __init__(
        self,
        *,
        broker_state_provider: BrokerStateProvider | None = None,
    ) -> None:
        self._broker_state_provider = broker_state_provider

    def reconcile(
        self,
        *,
        context: ServiceContext,
        expected_state: ExpectedTradingState,
        broker_state: BrokerReportedState | None = None,
    ) -> ReconciliationResult:
        actual_state = broker_state or self._load_broker_state()
        violations: list[ReconciliationViolation] = []

        expected_positions = {position.broker_position_id: position for position in expected_state.positions}
        for broker_position in actual_state.positions:
            if broker_position.broker_position_id not in expected_positions:
                violations.append(
                    ReconciliationViolation(
                        code="UNEXPECTED_BROKER_POSITION",
                        message="broker-reported position is not present in expected state.",
                        details={"broker_position_id": broker_position.broker_position_id},
                    )
                )

        in_sync = not violations
        status = ReconciliationStatus.IN_SYNC if in_sync else ReconciliationStatus.PANIC_STOP_REQUIRED
        escalation = EscalationDecision(
            target_halt_state=HaltState.ACTIVE if in_sync else HaltState.PANIC_STOP,
            safe_mode_requested=False,
            panic_stop_requested=not in_sync,
        )
        return ReconciliationResult(
            status=status,
            in_sync=in_sync,
            violations=tuple(violations),
            escalation=escalation,
        )

    def _load_broker_state(self) -> BrokerReportedState:
        if self._broker_state_provider is None:
            raise ValueError("broker_state_provider is required.")
        return self._broker_state_provider.get_broker_reported_state()
