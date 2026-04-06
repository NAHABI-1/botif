from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from mt5_platform_engine.strategy.base import StrategyBase
from mt5_platform_engine.strategy.models import FeatureInput, SignalAction, StrategySignal
from mt5_platform_engine.strategy.parameters import StrategyParameters, parameter_field


@dataclass(frozen=True, slots=True)
class RSIMeanReversionParameters(StrategyParameters):
    period: int = parameter_field(default=14, description="RSI period.", gt=0)
    oversold: Decimal = parameter_field(default=Decimal("30"), description="Oversold threshold.", gt=0)
    overbought: Decimal = parameter_field(default=Decimal("70"), description="Overbought threshold.", gt=0)


class RSIMeanReversionStrategy(StrategyBase[RSIMeanReversionParameters]):
    strategy_name = "rsi_mean_reversion"
    strategy_description = "RSI mean reversion."
    parameter_model = RSIMeanReversionParameters

    @property
    def minimum_bars(self) -> int:
        return self.parameters.period + 1

    def _evaluate(self, features: FeatureInput) -> StrategySignal:
        closes = [bar.close for bar in features.bars]
        gains = []
        losses = []
        for i in range(1, len(closes)):
            delta = closes[i] - closes[i - 1]
            gains.append(max(delta, Decimal("0")))
            losses.append(abs(min(delta, Decimal("0"))))
        avg_gain = sum(gains[-self.parameters.period :]) / Decimal(self.parameters.period)
        avg_loss = sum(losses[-self.parameters.period :]) / Decimal(self.parameters.period)
        rs = avg_gain / avg_loss if avg_loss > 0 else Decimal("100")
        rsi = Decimal("100") - (Decimal("100") / (Decimal("1") + rs))
        latest = features.latest_bar
        if rsi <= self.parameters.oversold:
            action = SignalAction.ENTER_LONG
        elif rsi >= self.parameters.overbought:
            action = SignalAction.ENTER_SHORT
        else:
            action = SignalAction.NO_ACTION
        return StrategySignal(
            strategy_name=self.strategy_name,
            symbol=features.symbol,
            action=action,
            generated_at=latest.closed_at,
            bar_index=len(features.bars) - 1,
            reason="rsi evaluation",
            entry_price=latest.close,
        )
