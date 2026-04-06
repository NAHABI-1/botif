from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def parameter_field(*, default: Any, description: str = "", gt: float | None = None) -> Any:
    metadata = {"description": description, "gt": gt}
    return field(default=default, metadata=metadata)


@dataclass(frozen=True, slots=True)
class StrategyParameters:
    """Base class for strategy parameter models."""
