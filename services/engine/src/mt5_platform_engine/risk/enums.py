from __future__ import annotations

from enum import Enum


class TradeSide(str, Enum):
    LONG = "long"
    SHORT = "short"


class GuardStatus(str, Enum):
    PASS = "pass"
    BLOCK = "block"


class HaltState(str, Enum):
    ACTIVE = "active"
    SAFE_MODE = "safe_mode"
    HALTED = "halted"
    PANIC_STOP = "panic_stop"


class ExposureMeasure(str, Enum):
    NOTIONAL = "notional"
    QUANTITY = "quantity"
    RISK = "risk"


class PositionSizingMethod(str, Enum):
    RISK_BASED = "risk_based"
    FIXED_QUANTITY = "fixed_quantity"


class SlippageReference(str, Enum):
    SIDE_QUOTE = "side_quote"
    MID = "mid"
