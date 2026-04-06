from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mt5_platform_engine.strategy.base import StrategyBase
from mt5_platform_engine.strategy.models import FeatureInput, SignalAction, StrategySignal
from mt5_platform_engine.strategy.parameters import StrategyParameters, parameter_field


@dataclass(frozen=True, slots=True)
class MovingAverageCrossoverParameters(StrategyParameters):
    fast_period: int = parameter_field(default=5, description="Fast MA period.", gt=0)
    slow_period: int = parameter_field(default=20, description="Slow MA period.", gt=0)


class MovingAverageCrossoverStrategy(StrategyBase[MovingAverageCrossoverParameters]):
    strategy_name = "moving_average_crossover"
    strategy_description = "Simple moving average crossover."
    parameter_model = MovingAverageCrossoverParameters

    @property
    def minimum_bars(self) -> int:
        return self.parameters.slow_period

    def _evaluate(self, features: FeatureInput) -> StrategySignal:
        closes = [bar.close for bar in features.bars]
        fast = sum(closes[-self.parameters.fast_period :]) / Decimal(self.parameters.fast_period)
        slow = sum(closes[-self.parameters.slow_period :]) / Decimal(self.parameters.slow_period)
        action = SignalAction.NO_ACTION
        if fast > slow:
            action = SignalAction.ENTER_LONG
        elif fast < slow:
            action = SignalAction.ENTER_SHORT
        return StrategySignal(
            strategy_name=self.strategy_name,
            symbol=features.symbol,
            action=action,
            generated_at=features.latest_bar.closed_at,
            bar_index=len(features.bars) - 1,
            reason="ma crossover",
            entry_price=features.latest_bar.close,
        )
