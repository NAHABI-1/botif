from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal

from mt5_platform_engine.risk.enums import GuardStatus, SlippageReference, TradeSide
from mt5_platform_engine.risk.models import (
    AccountRiskSnapshot,
    EmergencyFlags,
    GuardOutcome,
    MarketSnapshot,
    PanicStopActivation,
    PanicStopAssessment,
    PanicStopConfig,
    ProtectionLevels,
    SafeModeAssessment,
    SafeModeConfig,
    SlippageAssessment,
    SlippageToleranceConfig,
    TradeIntent,
)
from mt5_platform_engine.risk.types import BASIS_POINTS_DIVISOR, ONE, ZERO, min_enabled, safe_ratio


class StopLossTakeProfitPolicy(ABC):
    @abstractmethod
    def resolve(self, intent: TradeIntent) -> ProtectionLevels:
        raise NotImplementedError


class StaticProtectionPolicy(StopLossTakeProfitPolicy):
    def resolve(self, intent: TradeIntent) -> ProtectionLevels:
        if intent.stop_loss_price is None:
            raise ValueError("stop_loss_price is required.")
        return ProtectionLevels(stop_loss_price=intent.stop_loss_price, take_profit_price=intent.take_profit_price)


class SlippageTolerancePolicy(ABC):
    @abstractmethod
    def assess(self, intent: TradeIntent, market: MarketSnapshot | None) -> SlippageAssessment:
        raise NotImplementedError


class FixedSlippageTolerancePolicy(SlippageTolerancePolicy):
    def __init__(self, config: SlippageToleranceConfig) -> None:
        self._config = config

    def assess(self, intent: TradeIntent, market: MarketSnapshot | None) -> SlippageAssessment:
        if self._config.max_slippage is None and self._config.max_slippage_bps is None:
            return SlippageAssessment(
                status=GuardStatus.PASS,
                reference_price=None,
                requested_price=intent.entry_price,
                allowed_slippage=None,
                allowed_worst_price=None,
            )
        if market is None:
            status = GuardStatus.BLOCK if self._config.block_on_missing_market_data else GuardStatus.PASS
            return SlippageAssessment(
                status=status,
                reference_price=None,
                requested_price=intent.entry_price,
                allowed_slippage=None,
                allowed_worst_price=None,
                reason="market data is required for slippage validation." if status == GuardStatus.BLOCK else None,
            )
        reference_price = market.mid_price if self._config.reference_price == SlippageReference.MID else (
            market.ask_price if intent.side == TradeSide.LONG else market.bid_price
        )
        bps_limit = None
        if self._config.max_slippage_bps is not None:
            bps_limit = reference_price * self._config.max_slippage_bps / BASIS_POINTS_DIVISOR
        allowed_slippage = min_enabled(self._config.max_slippage, bps_limit)
        if allowed_slippage is None:
            return SlippageAssessment(
                status=GuardStatus.PASS,
                reference_price=reference_price,
                requested_price=intent.entry_price,
                allowed_slippage=None,
                allowed_worst_price=None,
            )
        difference = abs(intent.entry_price - reference_price)
        status = GuardStatus.BLOCK if difference > allowed_slippage else GuardStatus.PASS
        return SlippageAssessment(
            status=status,
            reference_price=reference_price,
            requested_price=intent.entry_price,
            allowed_slippage=allowed_slippage,
            allowed_worst_price=reference_price + allowed_slippage,
            observed_slippage=difference,
            usage_ratio=safe_ratio(difference, allowed_slippage),
            reason=None if status == GuardStatus.PASS else "requested entry price exceeds slippage tolerance.",
        )


class SafeModePolicy:
    def __init__(self, config: SafeModeConfig) -> None:
        self._config = config

    def assess(
        self,
        *,
        spread_outcome: GuardOutcome | None,
        daily_loss_outcome: GuardOutcome,
        drawdown_outcome: GuardOutcome,
    ) -> SafeModeAssessment:
        if not self._config.enabled:
            return SafeModeAssessment(active=False, position_size_scale=ONE)
        reasons: list[str] = []
        if (
            self._config.daily_loss_warning_fraction is not None
            and daily_loss_outcome.usage_ratio is not None
            and daily_loss_outcome.usage_ratio >= self._config.daily_loss_warning_fraction
        ):
            reasons.append("daily loss usage is approaching the configured cap.")
        if (
            self._config.drawdown_warning_fraction is not None
            and drawdown_outcome.usage_ratio is not None
            and drawdown_outcome.usage_ratio >= self._config.drawdown_warning_fraction
        ):
            reasons.append("drawdown usage is approaching the configured cap.")
        if (
            spread_outcome is not None
            and self._config.spread_warning_fraction is not None
            and spread_outcome.usage_ratio is not None
            and spread_outcome.usage_ratio >= self._config.spread_warning_fraction
        ):
            reasons.append("spread usage is approaching the configured cap.")
        active = bool(reasons)
        return SafeModeAssessment(
            active=active,
            position_size_scale=self._config.position_size_scale if active else ONE,
            reasons=tuple(reasons),
        )


class PanicStopPolicy:
    def __init__(self, config: PanicStopConfig) -> None:
        self._config = config

    def assess(self, account: AccountRiskSnapshot, emergency_flags: EmergencyFlags) -> PanicStopAssessment:
        if not self._config.enabled:
            return PanicStopAssessment(triggered=False)
        activations: list[PanicStopActivation] = []
        if self._config.manual_trigger_enabled and emergency_flags.panic_stop_requested:
            activations.append(
                PanicStopActivation(
                    code="manual_panic_stop",
                    description="manual panic stop was requested by an external operator.",
                )
            )
        if self._config.drawdown_fraction_trigger is not None:
            drawdown_fraction = safe_ratio(max(ZERO, account.peak_equity - account.equity), account.peak_equity)
            if drawdown_fraction is not None and drawdown_fraction >= self._config.drawdown_fraction_trigger:
                activations.append(
                    PanicStopActivation(
                        code="drawdown_fraction_trigger",
                        description="drawdown fraction exceeded the panic-stop threshold.",
                        observed_value=drawdown_fraction,
                        threshold_value=self._config.drawdown_fraction_trigger,
                    )
                )
        if self._config.daily_loss_fraction_trigger is not None:
            daily_loss_fraction = safe_ratio(
                max(ZERO, -(account.realized_pnl_today + account.unrealized_pnl)),
                account.day_start_equity,
            )
            if daily_loss_fraction is not None and daily_loss_fraction >= self._config.daily_loss_fraction_trigger:
                activations.append(
                    PanicStopActivation(
                        code="daily_loss_fraction_trigger",
                        description="session loss fraction exceeded the panic-stop threshold.",
                        observed_value=daily_loss_fraction,
                        threshold_value=self._config.daily_loss_fraction_trigger,
                    )
                )
        return PanicStopAssessment(triggered=bool(activations), activations=tuple(activations))
