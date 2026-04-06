from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from mt5_platform_engine.risk.enums import TradeSide
from mt5_platform_engine.strategy.base import StrategyBase
from mt5_platform_engine.strategy.models import FeatureInput, SignalAction
from mt5_platform_engine.trading.models import TradePermissionDecision, TradePermissionRequest, TradingControlState
from mt5_platform_engine.trading.services import TradePermissionService
from mt5_platform_worker.broker.interfaces import BrokerAdapter
from mt5_platform_worker.broker.models import MarketOrderRequest, TickQuote
from mt5_platform_worker.forward_testing.models import ForwardCycleResult, ForwardExecutionMode, ForwardExecutionRecord, ForwardSessionConfig, ForwardTestReport


@dataclass(slots=True)
class ForwardCycleInput:
    observed_at: datetime
    features: FeatureInput
    tick: TickQuote


class ForwardSessionRunner:
    def __init__(
        self,
        *,
        config: ForwardSessionConfig,
        strategy: StrategyBase,
        trade_permission_service: TradePermissionService,
        broker_adapter: BrokerAdapter | None = None,
    ) -> None:
        self._config = config
        self._strategy = strategy
        self._trade_permission_service = trade_permission_service
        self._broker_adapter = broker_adapter

    def run_session(self, cycles: list[ForwardCycleInput]) -> ForwardTestReport:
        results: list[ForwardCycleResult] = []
        for cycle in cycles:
            signal = self._strategy.evaluate(cycle.features)
            decision: TradePermissionDecision | None = None
            execution = None
            if signal.action in {SignalAction.ENTER_LONG, SignalAction.ENTER_SHORT}:
                side = TradeSide.LONG if signal.action == SignalAction.ENTER_LONG else TradeSide.SHORT
                if self._broker_adapter is not None:
                    request = MarketOrderRequest(symbol=self._config.symbol, side=side, volume=Decimal("1.0"))
                    _ = request
                    execution = ForwardExecutionRecord(
                        mode=self._config.mode,
                        signal_action=signal.action.value,
                        attempted=True,
                        success=True,
                        requested_side=side,
                        requested_quantity=Decimal("1.0"),
                        requested_price=cycle.tick.ask,
                        occurred_at=cycle.observed_at,
                        synthetic=self._config.mode == ForwardExecutionMode.PAPER,
                    )
            results.append(
                ForwardCycleResult(
                    observed_at=cycle.observed_at,
                    signal=signal,
                    permission_decision=decision,
                    execution=execution,
                )
            )
        return ForwardTestReport(config=self._config, cycles=tuple(results))
