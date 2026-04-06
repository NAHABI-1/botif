from __future__ import annotations

from decimal import Decimal

BASIS_POINTS_DIVISOR = Decimal("10000")
ZERO = Decimal("0")
ONE = Decimal("1")


def ensure_positive(value: Decimal, *, name: str) -> Decimal:
    if value <= ZERO:
        raise ValueError(f"{name} must be positive.")
    return value


def ensure_non_negative(value: Decimal, *, name: str) -> Decimal:
    if value < ZERO:
        raise ValueError(f"{name} must be non-negative.")
    return value


def clamp_fraction(value: Decimal, *, name: str) -> Decimal:
    if value <= ZERO or value > ONE:
        raise ValueError(f"{name} must be greater than 0 and less than or equal to 1.")
    return value


def safe_ratio(numerator: Decimal, denominator: Decimal) -> Decimal | None:
    if denominator == ZERO:
        return None
    return numerator / denominator


def min_enabled(*values: Decimal | None) -> Decimal | None:
    enabled = [value for value in values if value is not None]
    return min(enabled) if enabled else None
