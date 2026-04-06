from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from mt5_platform_engine.risk.enums import TradeSide


@dataclass(frozen=True, slots=True)
class TradeJournalEntry:
    position_id: int
    symbol: str
    side: TradeSide
    quantity: Decimal
    entry_time: datetime
    exit_time: datetime
    entry_price: Decimal
    exit_price: Decimal
    gross_pnl: Decimal
    net_pnl: Decimal

    def to_dict(self) -> dict[str, object]:
        return {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "side": self.side.value,
            "quantity": format(self.quantity, "f"),
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat(),
            "entry_price": format(self.entry_price, "f"),
            "exit_price": format(self.exit_price, "f"),
            "gross_pnl": format(self.gross_pnl, "f"),
            "net_pnl": format(self.net_pnl, "f"),
        }


@dataclass(frozen=True, slots=True)
class EquityPoint:
    timestamp: datetime
    equity: Decimal

    def to_dict(self) -> dict[str, object]:
        return {"timestamp": self.timestamp.isoformat(), "equity": format(self.equity, "f")}


@dataclass(frozen=True, slots=True)
class PerformanceMetrics:
    total_return: float
    max_drawdown: float
    total_trades: int

    def to_dict(self) -> dict[str, object]:
        return {
            "total_return": self.total_return,
            "max_drawdown": self.max_drawdown,
            "total_trades": self.total_trades,
        }


@dataclass(frozen=True, slots=True)
class BacktestReport:
    strategy_name: str
    symbol: str
    timeframe: str
    started_at: datetime
    finished_at: datetime
    initial_cash: Decimal
    final_equity: Decimal
    trade_journal: tuple[TradeJournalEntry, ...]
    equity_curve: tuple[EquityPoint, ...]
    metrics: PerformanceMetrics

    def to_dict(self) -> dict[str, object]:
        return {
            "summary": {
                "strategy_name": self.strategy_name,
                "symbol": self.symbol,
                "timeframe": self.timeframe,
                "initial_cash": format(self.initial_cash, "f"),
                "final_equity": format(self.final_equity, "f"),
            },
            "trade_journal": [entry.to_dict() for entry in self.trade_journal],
            "equity_curve": [point.to_dict() for point in self.equity_curve],
            "metrics": self.metrics.to_dict(),
        }
