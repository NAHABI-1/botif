from __future__ import annotations

from decimal import Decimal

from mt5_platform_engine.risk.calculators import PerTradeRiskCalculator
from mt5_platform_engine.risk.enums import GuardStatus, HaltState
from mt5_platform_engine.risk.guards import (
    DailyLossCapGuard,
    LossStreakCooldownGuard,
    MaxCorrelatedExposureGuard,
    MaxDrawdownGuard,
    MaxExposurePerSymbolGuard,
    MaxOpenPositionsGuard,
    SpreadFilter,
)
from mt5_platform_engine.risk.models import (
    EmergencyFlags,
    GuardOutcome,
    InstrumentRiskProfile,
    MarketSnapshot,
    OpenPosition,
    PortfolioRiskSnapshot,
    ProtectionLevels,
    RiskEngineConfig,
    RiskEvaluation,
    TradeIntent,
    TradingHaltSignal,
)
from mt5_platform_engine.risk.policies import (
    FixedSlippageTolerancePolicy,
    PanicStopPolicy,
    SafeModePolicy,
    StaticProtectionPolicy,
    StopLossTakeProfitPolicy,
)
from mt5_platform_engine.risk.sizing import PositionSizer
from mt5_platform_engine.risk.state_machine import TradingHaltStateMachine
from mt5_platform_engine.risk.types import safe_ratio


class RiskEngine:
    def __init__(self, *, config: RiskEngineConfig, protection_policy: StopLossTakeProfitPolicy | None = None) -> None:
        self._config = config
        self._risk_calculator = PerTradeRiskCalculator()
        self._position_sizer = PositionSizer(self._risk_calculator)
        self._protection_policy = protection_policy or StaticProtectionPolicy()
        self._open_positions_guard = MaxOpenPositionsGuard(config.max_open_positions)
        self._symbol_exposure_guard = MaxExposurePerSymbolGuard(config.max_symbol_exposure)
        self._correlated_exposure_guard = MaxCorrelatedExposureGuard(config.max_correlated_exposure)
        self._spread_filter = SpreadFilter(config.spread_filter)
        self._slippage_policy = FixedSlippageTolerancePolicy(config.slippage_tolerance)
        self._cooldown_guard = LossStreakCooldownGuard(config.cooldown_after_loss_streak)
        self._daily_loss_guard = DailyLossCapGuard(config.daily_loss_cap)
        self._drawdown_guard = MaxDrawdownGuard(config.max_drawdown)
        self._safe_mode_policy = SafeModePolicy(config.safe_mode)
        self._panic_stop_policy = PanicStopPolicy(config.panic_stop)
        self._halt_state_machine = TradingHaltStateMachine(config.trading_halt)

    def evaluate(
        self,
        *,
        intent: TradeIntent,
        portfolio: PortfolioRiskSnapshot,
        instrument: InstrumentRiskProfile,
        market: MarketSnapshot | None = None,
        emergency_flags: EmergencyFlags | None = None,
    ) -> RiskEvaluation:
        flags = emergency_flags or EmergencyFlags()
        guard_outcomes: list[GuardOutcome] = []

        panic_stop = self._panic_stop_policy.assess(portfolio.account, flags)
        daily_loss_outcome = self._daily_loss_guard.evaluate(portfolio.account)
        drawdown_outcome = self._drawdown_guard.evaluate(portfolio.account)
        spread_outcome = self._spread_filter.evaluate(market)
        cooldown_outcome = self._cooldown_guard.evaluate(portfolio.loss_streak, intent.requested_at)
        slippage = self._slippage_policy.assess(intent, market)
        slippage_outcome = GuardOutcome(rule_name="slippage", status=slippage.status, reason=slippage.reason)

        guard_outcomes.extend([daily_loss_outcome, drawdown_outcome, spread_outcome, cooldown_outcome, slippage_outcome])

        safe_mode = self._safe_mode_policy.assess(
            spread_outcome=spread_outcome,
            daily_loss_outcome=daily_loss_outcome,
            drawdown_outcome=drawdown_outcome,
        )

        halt_signal = TradingHaltSignal(
            panic_stop_requested=panic_stop.triggered,
            halt_requested=flags.manual_halt_requested
            or daily_loss_outcome.status == GuardStatus.BLOCK
            or drawdown_outcome.status == GuardStatus.BLOCK,
            safe_mode_requested=safe_mode.active,
            manual_resume_requested=flags.manual_resume_requested,
        )
        halt_state = self._halt_state_machine.transition(portfolio.halt_state, halt_signal)

        protection = None
        try:
            protection = self._protection_policy.resolve(intent)
        except ValueError as exc:
            guard_outcomes.append(GuardOutcome(rule_name="protection", status=GuardStatus.BLOCK, reason=str(exc)))

        if halt_state in {HaltState.HALTED, HaltState.PANIC_STOP}:
            return RiskEvaluation(
                allowed=False,
                halt_state=halt_state,
                reasons=tuple(self._reasons_from_outcomes(guard_outcomes)),
                guard_outcomes=tuple(guard_outcomes),
                protection=protection,
                position_size=None,
                trade_risk=None,
                safe_mode=safe_mode,
                slippage=slippage,
                panic_stop=panic_stop,
            )

        if protection is None or self._has_blocking_outcome(guard_outcomes):
            return RiskEvaluation(
                allowed=False,
                halt_state=halt_state,
                reasons=tuple(self._reasons_from_outcomes(guard_outcomes)),
                guard_outcomes=tuple(guard_outcomes),
                protection=protection,
                position_size=None,
                trade_risk=None,
                safe_mode=safe_mode,
                slippage=slippage,
                panic_stop=panic_stop,
            )

        risk_fraction_scale = safe_mode.position_size_scale if halt_state == HaltState.SAFE_MODE else Decimal("1")
        position_size = self._position_sizer.size(
            intent=intent,
            protection=protection,
            account=portfolio.account,
            instrument=instrument,
            sizing_config=self._config.position_sizing,
            per_trade_config=self._config.per_trade,
            risk_fraction_scale=risk_fraction_scale,
        )
        if position_size.status == GuardStatus.BLOCK:
            guard_outcomes.append(
                GuardOutcome(
                    rule_name="position_sizing",
                    status=GuardStatus.BLOCK,
                    reason=position_size.reason,
                )
            )
            return RiskEvaluation(
                allowed=False,
                halt_state=halt_state,
                reasons=tuple(self._reasons_from_outcomes(guard_outcomes)),
                guard_outcomes=tuple(guard_outcomes),
                protection=protection,
                position_size=position_size,
                trade_risk=None,
                safe_mode=safe_mode,
                slippage=slippage,
                panic_stop=panic_stop,
            )

        trade_risk = self._risk_calculator.calculate(
            intent=intent,
            protection=protection,
            quantity=position_size.quantity or Decimal("0"),
            instrument=instrument,
        )
        candidate_position = OpenPosition(
            symbol=intent.symbol,
            side=intent.side,
            quantity=trade_risk.quantity,
            entry_price=intent.entry_price,
            current_price=market.mid_price if market is not None else intent.entry_price,
            notional_exposure=trade_risk.notional_exposure,
            risk_amount=trade_risk.total_cash_risk,
            correlation_tags=intent.correlation_tags,
        )
        guard_outcomes.append(self._open_positions_guard.evaluate(portfolio))
        guard_outcomes.append(self._symbol_exposure_guard.evaluate(portfolio, candidate_position))
        guard_outcomes.extend(self._correlated_exposure_guard.evaluate(portfolio, candidate_position))

        allowed = not self._has_blocking_outcome(guard_outcomes)
        return RiskEvaluation(
            allowed=allowed,
            halt_state=halt_state,
            reasons=tuple(self._reasons_from_outcomes(guard_outcomes)),
            guard_outcomes=tuple(guard_outcomes),
            protection=protection,
            position_size=position_size,
            trade_risk=trade_risk,
            safe_mode=safe_mode,
            slippage=slippage,
            panic_stop=panic_stop,
        )

    @staticmethod
    def _has_blocking_outcome(outcomes: list[GuardOutcome]) -> bool:
        return any(outcome.status == GuardStatus.BLOCK for outcome in outcomes)

    @staticmethod
    def _reasons_from_outcomes(outcomes: list[GuardOutcome]) -> list[str]:
        reasons: list[str] = []
        for outcome in outcomes:
            if outcome.status == GuardStatus.BLOCK and outcome.reason:
                reasons.append(outcome.reason)
        return reasons
