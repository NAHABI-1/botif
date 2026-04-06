from __future__ import annotations

from mt5_platform_engine.risk.enums import HaltState
from mt5_platform_engine.risk.models import TradingHaltConfig, TradingHaltSignal


class TradingHaltStateMachine:
    def __init__(self, config: TradingHaltConfig) -> None:
        self._config = config

    def transition(self, current: HaltState, signal: TradingHaltSignal) -> HaltState:
        if signal.panic_stop_requested:
            return HaltState.PANIC_STOP
        if current == HaltState.PANIC_STOP:
            return HaltState.ACTIVE if signal.manual_resume_requested else HaltState.PANIC_STOP
        if signal.halt_requested:
            return HaltState.HALTED
        if current == HaltState.HALTED:
            return HaltState.ACTIVE if signal.manual_resume_requested else HaltState.HALTED
        if signal.safe_mode_requested and self._config.allow_safe_mode:
            return HaltState.SAFE_MODE
        return HaltState.ACTIVE
