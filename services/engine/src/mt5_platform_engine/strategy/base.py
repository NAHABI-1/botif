from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from mt5_platform_engine.strategy.models import FeatureInput, StrategySignal
from mt5_platform_engine.strategy.parameters import StrategyParameters

ParamsT = TypeVar("ParamsT", bound=StrategyParameters)


class StrategyBase(ABC, Generic[ParamsT]):
    strategy_name: str = "strategy"
    strategy_description: str = ""
    parameter_model: type[ParamsT] = StrategyParameters

    def __init__(self, parameters: ParamsT) -> None:
        self.parameters = parameters

    @property
    def minimum_bars(self) -> int:
        return 1

    def evaluate(self, features: FeatureInput) -> StrategySignal:
        if len(features.bars) < self.minimum_bars:
            return StrategySignal.no_signal(
                strategy_name=self.strategy_name,
                features=features,
                reason="insufficient bars",
            )
        return self._evaluate(features)

    @abstractmethod
    def _evaluate(self, features: FeatureInput) -> StrategySignal:
        raise NotImplementedError
