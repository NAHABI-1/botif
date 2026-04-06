from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum


class SignalAction(str, Enum):
    NO_ACTION = "no_action"
    ENTER_LONG = "enter_long"
    ENTER_SHORT = "enter_short"
    EXIT_LONG = "exit_long"
    EXIT_SHORT = "exit_short"


@dataclass(frozen=True, slots=True)
class FeatureBar:
    opened_at: datetime
    closed_at: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal


@dataclass(frozen=True, slots=True)
class FeatureInput:
    symbol: str
    timeframe: str
    bars: tuple[FeatureBar, ...]

    @property
    def latest_bar(self) -> FeatureBar:
        return self.bars[-1]


@dataclass(frozen=True, slots=True)
class StrategySignal:
    strategy_name: str
    symbol: str
    action: SignalAction
    generated_at: datetime
    bar_index: int
    reason: str
    entry_price: Decimal | None = None
    metadata: dict[str, object] = None

    @property
    def is_actionable(self) -> bool:
        return self.action != SignalAction.NO_ACTION

    @staticmethod
    def no_signal(*, strategy_name: str, features: FeatureInput, reason: str) -> "StrategySignal":
        return StrategySignal(
            strategy_name=strategy_name,
            symbol=features.symbol,
            action=SignalAction.NO_ACTION,
            generated_at=features.latest_bar.closed_at,
            bar_index=len(features.bars) - 1,
            reason=reason,
            entry_price=None,
            metadata={},
        )
