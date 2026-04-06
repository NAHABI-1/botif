from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mt5_platform_engine.strategy.base import StrategyBase
from mt5_platform_engine.strategy.models import FeatureInput, SignalAction, StrategySignal
from mt5_platform_engine.strategy.parameters import StrategyParameters, parameter_field


@dataclass(frozen=True, slots=True)
class BreakoutParameters(StrategyParameters):
    lookback: int = parameter_field(default=20, description="Breakout lookback bars.", gt=0)


class BreakoutStrategy(StrategyBase[BreakoutParameters]):
    strategy_name = "breakout"
    strategy_description = "Breakout above/below recent highs/lows."
    parameter_model = BreakoutParameters

    @property
    def minimum_bars(self) -> int:
        return self.parameters.lookback

    def _evaluate(self, features: FeatureInput) -> StrategySignal:
        bars = features.bars[-self.parameters.lookback :]
        highs = [bar.high for bar in bars]
        lows = [bar.low for bar in bars]
        latest = features.latest_bar
        if latest.close >= max(highs):
            action = SignalAction.ENTER_LONG
        elif latest.close <= min(lows):
            action = SignalAction.ENTER_SHORT
        else:
            action = SignalAction.NO_ACTION
        return StrategySignal(
            strategy_name=self.strategy_name,
            symbol=features.symbol,
            action=action,
            generated_at=latest.closed_at,
            bar_index=len(features.bars) - 1,
            reason="breakout evaluation",
            entry_price=latest.close,
        )
