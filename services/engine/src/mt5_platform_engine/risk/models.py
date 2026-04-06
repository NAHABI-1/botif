from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from decimal import Decimal

from mt5_platform_engine.risk.enums import ExposureMeasure, GuardStatus, HaltState, PositionSizingMethod, SlippageReference, TradeSide
from mt5_platform_engine.risk.types import clamp_fraction, ensure_non_negative, ensure_positive


@dataclass(frozen=True, slots=True)
class InstrumentRiskProfile:
    symbol: str
    quantity_step: Decimal
    min_quantity: Decimal
    max_quantity: Decimal | None
    risk_per_price_unit: Decimal
    notional_value_per_quantity: Decimal = Decimal("1")
    min_stop_distance: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required.")
        ensure_positive(self.quantity_step, name="quantity_step")
        ensure_positive(self.min_quantity, name="min_quantity")
        ensure_positive(self.risk_per_price_unit, name="risk_per_price_unit")
        ensure_positive(self.notional_value_per_quantity, name="notional_value_per_quantity")
        ensure_non_negative(self.min_stop_distance, name="min_stop_distance")


@dataclass(frozen=True, slots=True)
class ProtectionLevels:
    stop_loss_price: Decimal
    take_profit_price: Decimal | None = None

    def __post_init__(self) -> None:
        ensure_positive(self.stop_loss_price, name="stop_loss_price")
        if self.take_profit_price is not None:
            ensure_positive(self.take_profit_price, name="take_profit_price")


@dataclass(frozen=True, slots=True)
class TradeIntent:
    symbol: str
    side: TradeSide
    entry_price: Decimal
    requested_at: datetime
    stop_loss_price: Decimal | None = None
    take_profit_price: Decimal | None = None
    requested_quantity: Decimal | None = None
    correlation_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required.")
        ensure_positive(self.entry_price, name="entry_price")
        if self.requested_quantity is not None:
            ensure_positive(self.requested_quantity, name="requested_quantity")


@dataclass(frozen=True, slots=True)
class OpenPosition:
    symbol: str
    side: TradeSide
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    notional_exposure: Decimal
    risk_amount: Decimal
    correlation_tags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required.")
        ensure_positive(self.quantity, name="quantity")
        ensure_positive(self.entry_price, name="entry_price")
        ensure_positive(self.current_price, name="current_price")
        ensure_non_negative(self.notional_exposure, name="notional_exposure")
        ensure_non_negative(self.risk_amount, name="risk_amount")

    def exposure_for(self, measure: ExposureMeasure) -> Decimal:
        if measure == ExposureMeasure.NOTIONAL:
            return self.notional_exposure
        if measure == ExposureMeasure.QUANTITY:
            return self.quantity
        return self.risk_amount


@dataclass(frozen=True, slots=True)
class MarketSnapshot:
    symbol: str
    bid_price: Decimal
    ask_price: Decimal

    def __post_init__(self) -> None:
        if not self.symbol:
            raise ValueError("symbol is required.")
        ensure_positive(self.bid_price, name="bid_price")
        ensure_positive(self.ask_price, name="ask_price")
        if self.ask_price < self.bid_price:
            raise ValueError("ask_price must be >= bid_price.")

    @property
    def spread(self) -> Decimal:
        return self.ask_price - self.bid_price

    @property
    def mid_price(self) -> Decimal:
        return (self.bid_price + self.ask_price) / Decimal("2")


@dataclass(frozen=True, slots=True)
class AccountRiskSnapshot:
    equity: Decimal
    balance: Decimal
    day_start_equity: Decimal
    peak_equity: Decimal
    realized_pnl_today: Decimal
    unrealized_pnl: Decimal = Decimal("0")

    def __post_init__(self) -> None:
        ensure_positive(self.balance, name="balance")
        ensure_positive(self.day_start_equity, name="day_start_equity")
        ensure_positive(self.peak_equity, name="peak_equity")


@dataclass(frozen=True, slots=True)
class LossStreakSnapshot:
    consecutive_losses: int = 0
    last_loss_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.consecutive_losses < 0:
            raise ValueError("consecutive_losses must be non-negative.")


@dataclass(frozen=True, slots=True)
class EmergencyFlags:
    manual_halt_requested: bool = False
    manual_resume_requested: bool = False
    panic_stop_requested: bool = False


@dataclass(frozen=True, slots=True)
class PortfolioRiskSnapshot:
    account: AccountRiskSnapshot
    open_positions: tuple[OpenPosition, ...] = ()
    loss_streak: LossStreakSnapshot = field(default_factory=LossStreakSnapshot)
    halt_state: HaltState = HaltState.ACTIVE


@dataclass(frozen=True, slots=True)
class PositionSizingConfig:
    method: PositionSizingMethod = PositionSizingMethod.RISK_BASED
    fixed_quantity: Decimal | None = None

    def __post_init__(self) -> None:
        if self.method == PositionSizingMethod.FIXED_QUANTITY:
            if self.fixed_quantity is None:
                raise ValueError("fixed_quantity is required when method is fixed_quantity.")
            ensure_positive(self.fixed_quantity, name="fixed_quantity")
        elif self.fixed_quantity is not None:
            ensure_positive(self.fixed_quantity, name="fixed_quantity")


@dataclass(frozen=True, slots=True)
class PerTradeRiskConfig:
    max_fraction_of_equity: Decimal
    max_cash_risk: Decimal | None = None
    min_reward_to_risk: Decimal | None = None

    def __post_init__(self) -> None:
        clamp_fraction(self.max_fraction_of_equity, name="max_fraction_of_equity")
        if self.max_cash_risk is not None:
            ensure_positive(self.max_cash_risk, name="max_cash_risk")
        if self.min_reward_to_risk is not None:
            ensure_positive(self.min_reward_to_risk, name="min_reward_to_risk")


@dataclass(frozen=True, slots=True)
class MaxOpenPositionsConfig:
    max_open_positions: int | None = None


@dataclass(frozen=True, slots=True)
class MaxSymbolExposureConfig:
    max_exposure: Decimal | None = None
    measure: ExposureMeasure = ExposureMeasure.NOTIONAL


@dataclass(frozen=True, slots=True)
class CorrelationGroupConfig:
    name: str
    max_exposure: Decimal
    symbols: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    measure: ExposureMeasure = ExposureMeasure.NOTIONAL


@dataclass(frozen=True, slots=True)
class MaxCorrelatedExposureConfig:
    groups: tuple[CorrelationGroupConfig, ...] = ()


@dataclass(frozen=True, slots=True)
class SpreadFilterConfig:
    max_spread: Decimal | None = None
    max_spread_bps: Decimal | None = None
    block_on_missing_market_data: bool = True

    def __post_init__(self) -> None:
        if self.max_spread is not None:
            ensure_positive(self.max_spread, name="max_spread")
        if self.max_spread_bps is not None:
            ensure_positive(self.max_spread_bps, name="max_spread_bps")


@dataclass(frozen=True, slots=True)
class SlippageToleranceConfig:
    max_slippage: Decimal | None = None
    max_slippage_bps: Decimal | None = None
    reference_price: SlippageReference = SlippageReference.SIDE_QUOTE
    block_on_missing_market_data: bool = True


@dataclass(frozen=True, slots=True)
class LossStreakCooldownTier:
    loss_streak_threshold: int
    cooldown: timedelta


@dataclass(frozen=True, slots=True)
class CooldownAfterLossStreakConfig:
    tiers: tuple[LossStreakCooldownTier, ...] = ()


@dataclass(frozen=True, slots=True)
class DailyLossCapConfig:
    max_loss_amount: Decimal | None = None
    max_loss_fraction_of_day_start_equity: Decimal | None = None
    include_unrealized_pnl: bool = False


@dataclass(frozen=True, slots=True)
class MaxDrawdownConfig:
    max_drawdown_amount: Decimal | None = None
    max_drawdown_fraction: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SafeModeConfig:
    enabled: bool = True
    position_size_scale: Decimal = Decimal("0.5")
    daily_loss_warning_fraction: Decimal | None = Decimal("0.8")
    drawdown_warning_fraction: Decimal | None = Decimal("0.8")
    spread_warning_fraction: Decimal | None = Decimal("0.8")


@dataclass(frozen=True, slots=True)
class TradingHaltConfig:
    allow_safe_mode: bool = True
    require_manual_resume_after_halt: bool = True
    require_manual_resume_after_panic: bool = True


@dataclass(frozen=True, slots=True)
class PanicStopConfig:
    enabled: bool = True
    manual_trigger_enabled: bool = True
    drawdown_fraction_trigger: Decimal | None = None
    daily_loss_fraction_trigger: Decimal | None = None


@dataclass(frozen=True, slots=True)
class RiskEngineConfig:
    position_sizing: PositionSizingConfig
    per_trade: PerTradeRiskConfig
    max_open_positions: MaxOpenPositionsConfig = field(default_factory=MaxOpenPositionsConfig)
    max_symbol_exposure: MaxSymbolExposureConfig = field(default_factory=MaxSymbolExposureConfig)
    max_correlated_exposure: MaxCorrelatedExposureConfig = field(default_factory=MaxCorrelatedExposureConfig)
    spread_filter: SpreadFilterConfig = field(default_factory=SpreadFilterConfig)
    slippage_tolerance: SlippageToleranceConfig = field(default_factory=SlippageToleranceConfig)
    cooldown_after_loss_streak: CooldownAfterLossStreakConfig = field(default_factory=CooldownAfterLossStreakConfig)
    daily_loss_cap: DailyLossCapConfig = field(default_factory=DailyLossCapConfig)
    max_drawdown: MaxDrawdownConfig = field(default_factory=MaxDrawdownConfig)
    safe_mode: SafeModeConfig = field(default_factory=SafeModeConfig)
    trading_halt: TradingHaltConfig = field(default_factory=TradingHaltConfig)
    panic_stop: PanicStopConfig = field(default_factory=PanicStopConfig)


@dataclass(frozen=True, slots=True)
class GuardOutcome:
    rule_name: str
    status: GuardStatus
    reason: str | None = None
    current_value: Decimal | None = None
    projected_value: Decimal | None = None
    limit_value: Decimal | None = None
    usage_ratio: Decimal | None = None
    blocked_until: datetime | None = None


@dataclass(frozen=True, slots=True)
class SlippageAssessment:
    status: GuardStatus
    reference_price: Decimal | None
    requested_price: Decimal
    allowed_slippage: Decimal | None
    allowed_worst_price: Decimal | None
    observed_slippage: Decimal | None = None
    usage_ratio: Decimal | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class PositionSizeResult:
    status: GuardStatus
    quantity: Decimal | None
    allowed_cash_risk: Decimal | None = None
    estimated_cash_risk: Decimal | None = None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class TradeRiskSummary:
    quantity: Decimal
    notional_exposure: Decimal
    total_cash_risk: Decimal
    risk_reward_ratio: Decimal | None = None


@dataclass(frozen=True, slots=True)
class SafeModeAssessment:
    active: bool
    position_size_scale: Decimal
    reasons: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class PanicStopActivation:
    code: str
    description: str
    observed_value: Decimal | None = None
    threshold_value: Decimal | None = None


@dataclass(frozen=True, slots=True)
class PanicStopAssessment:
    triggered: bool
    activations: tuple[PanicStopActivation, ...] = ()


@dataclass(frozen=True, slots=True)
class TradingHaltSignal:
    panic_stop_requested: bool = False
    halt_requested: bool = False
    safe_mode_requested: bool = False
    manual_resume_requested: bool = False


@dataclass(frozen=True, slots=True)
class ProtectionOutcome:
    status: GuardStatus
    reason: str | None = None
    stop_loss: Decimal | None = None
    take_profit: Decimal | None = None


@dataclass(frozen=True, slots=True)
class RiskEvaluation:
    allowed: bool
    halt_state: HaltState
    reasons: tuple[str, ...]
    guard_outcomes: tuple[GuardOutcome, ...]
    protection: ProtectionLevels | None
    position_size: PositionSizeResult | None
    trade_risk: TradeRiskSummary | None
    safe_mode: SafeModeAssessment
    slippage: SlippageAssessment
    panic_stop: PanicStopAssessment
