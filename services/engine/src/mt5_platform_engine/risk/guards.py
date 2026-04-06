from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from mt5_platform_engine.risk.enums import ExposureMeasure, GuardStatus
from mt5_platform_engine.risk.models import (
    AccountRiskSnapshot,
    CooldownAfterLossStreakConfig,
    CorrelationGroupConfig,
    DailyLossCapConfig,
    GuardOutcome,
    LossStreakSnapshot,
    MarketSnapshot,
    MaxCorrelatedExposureConfig,
    MaxDrawdownConfig,
    MaxOpenPositionsConfig,
    MaxSymbolExposureConfig,
    OpenPosition,
    PortfolioRiskSnapshot,
    SpreadFilterConfig,
)
from mt5_platform_engine.risk.types import BASIS_POINTS_DIVISOR, ZERO, min_enabled, safe_ratio


class MaxOpenPositionsGuard:
    def __init__(self, config: MaxOpenPositionsConfig) -> None:
        self._config = config

    def evaluate(self, portfolio: PortfolioRiskSnapshot) -> GuardOutcome:
        if self._config.max_open_positions is None:
            return GuardOutcome(rule_name="max_open_positions", status=GuardStatus.PASS)
        current = Decimal(len(portfolio.open_positions))
        projected = current + Decimal("1")
        limit = Decimal(self._config.max_open_positions)
        status = GuardStatus.BLOCK if projected > limit else GuardStatus.PASS
        return GuardOutcome(
            rule_name="max_open_positions",
            status=status,
            current_value=current,
            projected_value=projected,
            limit_value=limit,
            usage_ratio=safe_ratio(projected, limit),
            reason=None if status == GuardStatus.PASS else "projected open positions exceed the configured maximum.",
        )


class MaxExposurePerSymbolGuard:
    def __init__(self, config: MaxSymbolExposureConfig) -> None:
        self._config = config

    def evaluate(self, portfolio: PortfolioRiskSnapshot, candidate: OpenPosition) -> GuardOutcome:
        if self._config.max_exposure is None:
            return GuardOutcome(rule_name="max_symbol_exposure", status=GuardStatus.PASS)
        current = sum(
            position.exposure_for(self._config.measure)
            for position in portfolio.open_positions
            if position.symbol == candidate.symbol
        )
        projected = current + candidate.exposure_for(self._config.measure)
        limit = self._config.max_exposure
        status = GuardStatus.BLOCK if projected > limit else GuardStatus.PASS
        return GuardOutcome(
            rule_name="max_symbol_exposure",
            status=status,
            current_value=current,
            projected_value=projected,
            limit_value=limit,
            usage_ratio=safe_ratio(projected, limit),
            reason=None if status == GuardStatus.PASS else "projected symbol exposure exceeds the configured maximum.",
        )


class MaxCorrelatedExposureGuard:
    def __init__(self, config: MaxCorrelatedExposureConfig) -> None:
        self._config = config

    def evaluate(self, portfolio: PortfolioRiskSnapshot, candidate: OpenPosition) -> tuple[GuardOutcome, ...]:
        outcomes: list[GuardOutcome] = []
        for group in self._config.groups:
            if not self._matches(group, candidate):
                continue
            current = sum(
                position.exposure_for(group.measure)
                for position in portfolio.open_positions
                if self._matches(group, position)
            )
            projected = current + candidate.exposure_for(group.measure)
            status = GuardStatus.BLOCK if projected > group.max_exposure else GuardStatus.PASS
            outcomes.append(
                GuardOutcome(
                    rule_name=f"max_correlated_exposure:{group.name}",
                    status=status,
                    current_value=current,
                    projected_value=projected,
                    limit_value=group.max_exposure,
                    usage_ratio=safe_ratio(projected, group.max_exposure),
                    reason=None if status == GuardStatus.PASS else "projected exposure exceeds correlated group.",
                )
            )
        return tuple(outcomes)

    @staticmethod
    def _matches(group: CorrelationGroupConfig, position: OpenPosition) -> bool:
        return position.symbol in group.symbols or bool(set(position.correlation_tags).intersection(group.tags))


class SpreadFilter:
    def __init__(self, config: SpreadFilterConfig) -> None:
        self._config = config

    def evaluate(self, market: MarketSnapshot | None) -> GuardOutcome:
        if self._config.max_spread is None and self._config.max_spread_bps is None:
            return GuardOutcome(rule_name="spread_filter", status=GuardStatus.PASS)
        if market is None:
            status = GuardStatus.BLOCK if self._config.block_on_missing_market_data else GuardStatus.PASS
            return GuardOutcome(
                rule_name="spread_filter",
                status=status,
                reason="market data is required for spread evaluation." if status == GuardStatus.BLOCK else None,
            )
        bps_limit = None
        if self._config.max_spread_bps is not None:
            bps_limit = market.mid_price * self._config.max_spread_bps / BASIS_POINTS_DIVISOR
        limit = min_enabled(self._config.max_spread, bps_limit)
        if limit is None:
            return GuardOutcome(rule_name="spread_filter", status=GuardStatus.PASS)
        spread = market.spread
        status = GuardStatus.BLOCK if spread > limit else GuardStatus.PASS
        return GuardOutcome(
            rule_name="spread_filter",
            status=status,
            current_value=spread,
            projected_value=spread,
            limit_value=limit,
            usage_ratio=safe_ratio(spread, limit),
            reason=None if status == GuardStatus.PASS else "market spread exceeds the configured maximum.",
        )


class LossStreakCooldownGuard:
    def __init__(self, config: CooldownAfterLossStreakConfig) -> None:
        self._tiers = tuple(sorted(config.tiers, key=lambda tier: tier.loss_streak_threshold, reverse=True))

    def evaluate(self, loss_streak: LossStreakSnapshot, as_of: datetime) -> GuardOutcome:
        if loss_streak.consecutive_losses == 0 or not self._tiers:
            return GuardOutcome(rule_name="loss_streak_cooldown", status=GuardStatus.PASS)
        tier = next(
            (
                configured_tier
                for configured_tier in self._tiers
                if loss_streak.consecutive_losses >= configured_tier.loss_streak_threshold
            ),
            None,
        )
        if tier is None or loss_streak.last_loss_at is None:
            return GuardOutcome(rule_name="loss_streak_cooldown", status=GuardStatus.PASS)
        blocked_until = loss_streak.last_loss_at + tier.cooldown
        status = GuardStatus.BLOCK if as_of < blocked_until else GuardStatus.PASS
        return GuardOutcome(
            rule_name="loss_streak_cooldown",
            status=status,
            blocked_until=blocked_until if status == GuardStatus.BLOCK else None,
            reason=None if status == GuardStatus.PASS else "loss-streak cooldown is active.",
        )


class DailyLossCapGuard:
    def __init__(self, config: DailyLossCapConfig) -> None:
        self._config = config

    def evaluate(self, account: AccountRiskSnapshot) -> GuardOutcome:
        if self._config.max_loss_amount is None and self._config.max_loss_fraction_of_day_start_equity is None:
            return GuardOutcome(rule_name="daily_loss_cap", status=GuardStatus.PASS)
        session_pnl = account.realized_pnl_today
        if self._config.include_unrealized_pnl:
            session_pnl += account.unrealized_pnl
        loss_amount = max(ZERO, -session_pnl)
        limit = self._config.max_loss_amount
        if self._config.max_loss_fraction_of_day_start_equity is not None:
            limit = min_enabled(limit, account.day_start_equity * self._config.max_loss_fraction_of_day_start_equity)
        if limit is None:
            return GuardOutcome(rule_name="daily_loss_cap", status=GuardStatus.PASS)
        status = GuardStatus.BLOCK if loss_amount >= limit else GuardStatus.PASS
        return GuardOutcome(
            rule_name="daily_loss_cap",
            status=status,
            current_value=loss_amount,
            limit_value=limit,
            usage_ratio=safe_ratio(loss_amount, limit),
            reason=None if status == GuardStatus.PASS else "daily loss cap reached.",
        )


class MaxDrawdownGuard:
    def __init__(self, config: MaxDrawdownConfig) -> None:
        self._config = config

    def evaluate(self, account: AccountRiskSnapshot) -> GuardOutcome:
        if self._config.max_drawdown_amount is None and self._config.max_drawdown_fraction is None:
            return GuardOutcome(rule_name="max_drawdown", status=GuardStatus.PASS)
        drawdown = max(ZERO, account.peak_equity - account.equity)
        limit = self._config.max_drawdown_amount
        if self._config.max_drawdown_fraction is not None:
            limit = min_enabled(limit, account.peak_equity * self._config.max_drawdown_fraction)
        if limit is None:
            return GuardOutcome(rule_name="max_drawdown", status=GuardStatus.PASS)
        status = GuardStatus.BLOCK if drawdown >= limit else GuardStatus.PASS
        return GuardOutcome(
            rule_name="max_drawdown",
            status=status,
            current_value=drawdown,
            limit_value=limit,
            usage_ratio=safe_ratio(drawdown, limit),
            reason=None if status == GuardStatus.PASS else "drawdown cap reached.",
        )
