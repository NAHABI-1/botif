from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Mapping

from mt5_platform_engine.risk.enums import TradeSide
from mt5_platform_engine.risk.models import AccountRiskSnapshot, InstrumentRiskProfile, MarketSnapshot, TradeIntent


class RetcodeCategory(str, Enum):
    SUCCESS = "success"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class BrokerRetcode:
    code: int
    name: str
    category: RetcodeCategory
    description: str
    is_success: bool
    is_retryable: bool


@dataclass(frozen=True, slots=True)
class ConnectionStatus:
    initialized: bool
    logged_in: bool
    login: int | None = None
    server: str | None = None
    last_error_code: int | None = None
    last_error_description: str | None = None


@dataclass(frozen=True, slots=True)
class SymbolMetadata:
    symbol: str
    visible: bool
    digits: int
    point: Decimal
    volume_min: Decimal
    volume_max: Decimal
    volume_step: Decimal
    trade_contract_size: Decimal
    trade_tick_size: Decimal
    trade_tick_value: Decimal
    stops_level_points: int = 0
    freeze_level_points: int = 0

    def to_instrument_risk_profile(self) -> InstrumentRiskProfile:
        max_quantity = self.volume_max if self.volume_max > Decimal("0") else None
        return InstrumentRiskProfile(
            symbol=self.symbol,
            quantity_step=self.volume_step,
            min_quantity=self.volume_min,
            max_quantity=max_quantity,
            risk_per_price_unit=self.trade_tick_value / self.trade_tick_size,
            notional_value_per_quantity=self.trade_contract_size,
            min_stop_distance=self.point * Decimal(self.stops_level_points),
        )


@dataclass(frozen=True, slots=True)
class TickQuote:
    symbol: str
    observed_at: datetime
    bid: Decimal
    ask: Decimal
    last: Decimal | None = None

    def to_market_snapshot(self) -> MarketSnapshot:
        return MarketSnapshot(symbol=self.symbol, bid_price=self.bid, ask_price=self.ask)


@dataclass(frozen=True, slots=True)
class RatesQuery:
    symbol: str
    timeframe: str
    start_pos: int = 0
    count: int = 1


@dataclass(frozen=True, slots=True)
class AccountSnapshot:
    login: int
    server: str | None
    currency: str | None
    balance: Decimal
    equity: Decimal
    margin: Decimal
    free_margin: Decimal
    profit: Decimal

    def to_risk_snapshot(self) -> AccountRiskSnapshot:
        return AccountRiskSnapshot(
            equity=self.equity,
            balance=self.balance,
            day_start_equity=self.equity,
            peak_equity=self.equity,
            realized_pnl_today=self.profit,
        )


@dataclass(frozen=True, slots=True)
class MarketOrderRequest:
    symbol: str
    side: TradeSide
    volume: Decimal
    price: Decimal | None = None
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None
    magic_number: int | None = None
    comment: str | None = None


@dataclass(frozen=True, slots=True)
class PreparedOrderRequest:
    operation: str
    symbol: str
    payload: Mapping[str, object]
    comment: str | None = None


@dataclass(frozen=True, slots=True)
class OrderSendResult:
    request: PreparedOrderRequest
    retcode: BrokerRetcode
    broker_comment: str | None
    occurred_at: datetime
    order_ticket: int | None = None
    deal_ticket: int | None = None
    executed_volume: Decimal | None = None
    executed_price: Decimal | None = None
    raw: Mapping[str, object] | None = None

    @property
    def success(self) -> bool:
        return self.retcode.is_success


def ensure_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
