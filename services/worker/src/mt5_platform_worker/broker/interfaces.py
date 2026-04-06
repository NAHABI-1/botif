from __future__ import annotations

from typing import Protocol

from mt5_platform_worker.broker.models import AccountSnapshot, MarketOrderRequest, OrderSendResult, RatesQuery, SymbolMetadata, TickQuote


class BrokerAdapter(Protocol):
    def initialize(self):
        ...

    def login(self):
        ...

    def connect(self):
        ...

    def shutdown(self) -> None:
        ...

    def get_symbol_metadata(self, symbol: str, *, ensure_visible: bool = True) -> SymbolMetadata:
        ...

    def get_latest_tick(self, symbol: str) -> TickQuote:
        ...

    def get_rates(self, query: RatesQuery):
        ...

    def send_market_order(self, request: MarketOrderRequest) -> OrderSendResult:
        ...

    def get_account_snapshot(self) -> AccountSnapshot:
        ...
