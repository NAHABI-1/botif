from __future__ import annotations

from decimal import Decimal

from mt5_platform_engine.backtesting.models import EquityPoint, PerformanceMetrics, TradeJournalEntry


def calculate_performance_metrics(
    *,
    initial_cash: Decimal,
    trade_journal: tuple[TradeJournalEntry, ...],
    equity_curve: tuple[EquityPoint, ...],
) -> PerformanceMetrics:
    final_equity = equity_curve[-1].equity if equity_curve else initial_cash
    total_return = float((final_equity - initial_cash) / initial_cash) if initial_cash > 0 else 0.0
    peak = initial_cash
    max_drawdown = 0.0
    for point in equity_curve:
        if point.equity > peak:
            peak = point.equity
        drawdown = float((peak - point.equity) / peak) if peak > 0 else 0.0
        max_drawdown = max(max_drawdown, drawdown)
    return PerformanceMetrics(
        total_return=total_return,
        max_drawdown=max_drawdown,
        total_trades=len(trade_journal),
    )
