from __future__ import annotations

from decimal import Decimal, ROUND_DOWN

from mt5_platform_engine.risk.calculators import PerTradeRiskCalculator
from mt5_platform_engine.risk.enums import GuardStatus, PositionSizingMethod
from mt5_platform_engine.risk.models import (
    AccountRiskSnapshot,
    InstrumentRiskProfile,
    PerTradeRiskConfig,
    PositionSizeResult,
    PositionSizingConfig,
    ProtectionLevels,
    TradeIntent,
)
from mt5_platform_engine.risk.types import ZERO, safe_ratio


class PositionSizer:
    def __init__(self, calculator: PerTradeRiskCalculator) -> None:
        self._calculator = calculator

    def size(
        self,
        *,
        intent: TradeIntent,
        protection: ProtectionLevels,
        account: AccountRiskSnapshot,
        instrument: InstrumentRiskProfile,
        sizing_config: PositionSizingConfig,
        per_trade_config: PerTradeRiskConfig,
        risk_fraction_scale: Decimal = Decimal("1"),
    ) -> PositionSizeResult:
        if sizing_config.method == PositionSizingMethod.FIXED_QUANTITY:
            quantity = sizing_config.fixed_quantity
            if quantity is None:
                return PositionSizeResult(status=GuardStatus.BLOCK, quantity=None, reason="fixed quantity missing.")
            return PositionSizeResult(status=GuardStatus.PASS, quantity=quantity)

        max_fraction = per_trade_config.max_fraction_of_equity * risk_fraction_scale
        allowed_cash_risk = account.equity * max_fraction
        risk_distance = abs(intent.entry_price - protection.stop_loss_price)
        if risk_distance <= ZERO:
            return PositionSizeResult(status=GuardStatus.BLOCK, quantity=None, reason="invalid stop-loss distance.")

        raw_quantity = allowed_cash_risk / (risk_distance * instrument.risk_per_price_unit)
        step = instrument.quantity_step
        stepped = (raw_quantity / step).quantize(Decimal("1"), rounding=ROUND_DOWN) * step
        if stepped < instrument.min_quantity:
            return PositionSizeResult(
                status=GuardStatus.BLOCK,
                quantity=None,
                allowed_cash_risk=allowed_cash_risk,
                estimated_cash_risk=allowed_cash_risk,
                reason="sized quantity below minimum.",
            )
        if instrument.max_quantity is not None and stepped > instrument.max_quantity:
            stepped = instrument.max_quantity

        return PositionSizeResult(
            status=GuardStatus.PASS,
            quantity=stepped,
            allowed_cash_risk=allowed_cash_risk,
            estimated_cash_risk=allowed_cash_risk,
        )
