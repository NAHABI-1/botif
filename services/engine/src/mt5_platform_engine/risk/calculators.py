from __future__ import annotations

from decimal import Decimal

from mt5_platform_engine.risk.enums import TradeSide
from mt5_platform_engine.risk.models import InstrumentRiskProfile, ProtectionLevels, TradeIntent, TradeRiskSummary


class PerTradeRiskCalculator:
    def calculate(
        self,
        *,
        intent: TradeIntent,
        protection: ProtectionLevels,
        quantity: Decimal,
        instrument: InstrumentRiskProfile,
    ) -> TradeRiskSummary:
        risk_distance = abs(intent.entry_price - protection.stop_loss_price)
        total_cash_risk = risk_distance * instrument.risk_per_price_unit * quantity
        notional_exposure = instrument.notional_value_per_quantity * quantity
        risk_reward = None
        if protection.take_profit_price is not None and risk_distance > Decimal("0"):
            reward_distance = abs(protection.take_profit_price - intent.entry_price)
            risk_reward = reward_distance / risk_distance
        return TradeRiskSummary(
            quantity=quantity,
            notional_exposure=notional_exposure,
            total_cash_risk=total_cash_risk,
            risk_reward_ratio=risk_reward,
        )
