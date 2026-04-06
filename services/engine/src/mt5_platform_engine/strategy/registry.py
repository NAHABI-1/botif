from __future__ import annotations

from typing import Type

from mt5_platform_engine.strategy.base import StrategyBase
from mt5_platform_engine.strategy.parameters import StrategyParameters


class StrategyRegistry:
    def __init__(self) -> None:
        self._strategies: dict[str, Type[StrategyBase[StrategyParameters]]] = {}

    def register(self, strategy: Type[StrategyBase[StrategyParameters]]) -> None:
        self._strategies[strategy.strategy_name] = strategy

    def get(self, name: str) -> Type[StrategyBase[StrategyParameters]] | None:
        return self._strategies.get(name)

    def list(self) -> tuple[str, ...]:
        return tuple(self._strategies.keys())
