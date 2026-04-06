from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from mt5_platform_engine.backtesting.metrics import calculate_performance_metrics
from mt5_platform_engine.backtesting.models import BacktestReport, EquityPoint, TradeJournalEntry
from mt5_platform_engine.risk.enums import TradeSide
from mt5_platform_engine.strategy.base import StrategyBase
from mt5_platform_engine.strategy.models import FeatureInput, SignalAction


@dataclass(frozen=True, slots=True)
class BacktestConfig:
    initial_cash: Decimal = Decimal("10000")


@dataclass(frozen=True, slots=True)
class BacktestRequest:
    strategy: StrategyBase
    features: FeatureInput
    config: BacktestConfig


class BacktestRunner:
    def run(self, request: BacktestRequest) -> BacktestReport:
        strategy = request.strategy
        features = request.features
        cash = request.config.initial_cash
        equity_curve: list[EquityPoint] = []
        trade_journal: list[TradeJournalEntry] = []
        open_position = None

        for idx, bar in enumerate(features.bars):
            window = FeatureInput(symbol=features.symbol, timeframe=features.timeframe, bars=features.bars[: idx + 1])
            signal = strategy.evaluate(window)
            if signal.action == SignalAction.ENTER_LONG and open_position is None:
                open_position = (TradeSide.LONG, bar.close, bar.closed_at)
            elif signal.action == SignalAction.ENTER_SHORT and open_position is None:
                open_position = (TradeSide.SHORT, bar.close, bar.closed_at)
            elif signal.action in {SignalAction.EXIT_LONG, SignalAction.EXIT_SHORT} and open_position is not None:
                side, entry_price, entry_time = open_position
                pnl = bar.close - entry_price if side == TradeSide.LONG else entry_price - bar.close
                cash += pnl
                trade_journal.append(
                    TradeJournalEntry(
                        position_id=len(trade_journal) + 1,
                        symbol=features.symbol,
                        side=side,
                        quantity=Decimal("1"),
                        entry_time=entry_time,
                        exit_time=bar.closed_at,
                        entry_price=entry_price,
                        exit_price=bar.close,
                        gross_pnl=pnl,
                        net_pnl=pnl,
                    )
                )
                open_position = None
            equity_curve.append(EquityPoint(timestamp=bar.closed_at, equity=cash))

        metrics = calculate_performance_metrics(
            initial_cash=request.config.initial_cash,
            trade_journal=tuple(trade_journal),
            equity_curve=tuple(equity_curve),
        )
        return BacktestReport(
            strategy_name=strategy.strategy_name,
            symbol=features.symbol,
            timeframe=features.timeframe,
            started_at=features.bars[0].opened_at,
            finished_at=features.bars[-1].closed_at,
            initial_cash=request.config.initial_cash,
            final_equity=equity_curve[-1].equity if equity_curve else request.config.initial_cash,
            trade_journal=tuple(trade_journal),
            equity_curve=tuple(equity_curve),
            metrics=metrics,
        )
