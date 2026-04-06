from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any

from mt5_platform_worker.broker.exceptions import MT5DependencyError, MT5InitializationError, MT5LoginError, MT5OrderSendError
from mt5_platform_worker.broker.interfaces import BrokerAdapter
from mt5_platform_worker.broker.models import (
    BrokerRetcode,
    ConnectionStatus,
    MarketOrderRequest,
    OrderSendResult,
    PreparedOrderRequest,
    RetcodeCategory,
    SymbolMetadata,
    TickQuote,
)


def load_mt5_module() -> Any:
    try:
        import MetaTrader5 as mt5  # type: ignore[import-not-found]
    except ImportError as exc:
        raise MT5DependencyError("MetaTrader5 Python package is not installed.") from exc
    return mt5


class MT5BrokerAdapter(BrokerAdapter):
    def __init__(self, *, module: Any | None = None, logger: logging.Logger | None = None) -> None:
        self._module = module
        self._logger = logger or logging.getLogger(__name__)
        self._initialized = False
        self._logged_in = False

    def _mt5(self) -> Any:
        if self._module is None:
            self._module = load_mt5_module()
        return self._module

    def initialize(self) -> ConnectionStatus:
        ok = self._mt5().initialize()
        if not ok:
            code, desc = self._mt5().last_error()
            raise MT5InitializationError("MT5 initialize failed", operation="initialize", last_error_code=code, last_error_description=desc)
        self._initialized = True
        return ConnectionStatus(initialized=True, logged_in=self._logged_in)

    def login(self) -> ConnectionStatus:
        ok = self._mt5().login()
        if not ok:
            code, desc = self._mt5().last_error()
            raise MT5LoginError("MT5 login failed", operation="login", last_error_code=code, last_error_description=desc)
        self._logged_in = True
        return ConnectionStatus(initialized=self._initialized, logged_in=True)

    def connect(self) -> ConnectionStatus:
        status = self.initialize()
        return status

    def shutdown(self) -> None:
        if self._module is not None:
            self._module.shutdown()
        self._initialized = False
        self._logged_in = False

    def get_symbol_metadata(self, symbol: str, *, ensure_visible: bool = True) -> SymbolMetadata:
        info = self._mt5().symbol_info(symbol)
        if info is None:
            raise MT5OrderSendError(f"Symbol not found: {symbol}", operation="symbol_info")
        return SymbolMetadata(
            symbol=info.name,
            visible=bool(info.visible),
            digits=int(info.digits),
            point=float(info.point),
            volume_min=float(info.volume_min),
            volume_max=float(info.volume_max),
            volume_step=float(info.volume_step),
            trade_contract_size=float(info.trade_contract_size),
            trade_tick_size=float(info.trade_tick_size),
            trade_tick_value=float(info.trade_tick_value),
        )

    def get_latest_tick(self, symbol: str) -> TickQuote:
        tick = self._mt5().symbol_info_tick(symbol)
        if tick is None:
            raise MT5OrderSendError("tick unavailable", operation="symbol_info_tick")
        return TickQuote(
            symbol=symbol,
            observed_at=datetime.fromtimestamp(tick.time, tz=timezone.utc),
            bid=tick.bid,
            ask=tick.ask,
            last=tick.last,
        )

    def get_rates(self, query):
        return ()

    def send_market_order(self, request: MarketOrderRequest) -> OrderSendResult:
        payload = {"symbol": request.symbol}
        result = self._mt5().order_send(payload)
        if result is None:
            raise MT5OrderSendError("order_send failed", operation="order_send")
        retcode = BrokerRetcode(
            code=int(result.retcode),
            name="RET_CODE",
            category=RetcodeCategory.SUCCESS if int(result.retcode) == 10009 else RetcodeCategory.REJECTED,
            description=str(result.comment),
            is_success=int(result.retcode) == 10009,
            is_retryable=False,
        )
        return OrderSendResult(
            request=PreparedOrderRequest(operation="market_order", symbol=request.symbol, payload=payload),
            retcode=retcode,
            broker_comment=str(result.comment),
            occurred_at=datetime.now(timezone.utc),
        )

    def get_account_snapshot(self):
        account = self._mt5().account_info()
        if account is None:
            raise MT5OrderSendError("account_info failed", operation="account_info")
        from mt5_platform_worker.broker.models import AccountSnapshot

        return AccountSnapshot(
            login=account.login,
            server=account.server,
            currency=account.currency,
            balance=account.balance,
            equity=account.equity,
            margin=account.margin,
            free_margin=account.margin_free,
            profit=account.profit,
        )
