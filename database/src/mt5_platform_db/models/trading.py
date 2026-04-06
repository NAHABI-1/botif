from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mt5_platform_db.db.base import Base, CreatedTimestampMixin, UUIDPrimaryKeyMixin, UpdatedTimestampMixin, utc_now
from mt5_platform_db.db.enums import (
    OrderRequestStatus,
    OrderResultStatus,
    OrderSide,
    OrderType,
    PositionSide,
    PositionStatus,
    TimeInForce,
)
from mt5_platform_db.db.types import JSON_DOCUMENT, PRICE_NUMERIC, VOLUME_NUMERIC


class SignalEvent(UUIDPrimaryKeyMixin, CreatedTimestampMixin, Base):
    __tablename__ = "signal_events"
    __table_args__ = (
        Index("ix_signal_events_run_generated_at", "strategy_run_id", "generated_at"),
    )

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    strategy_config_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("strategy_configs.id"), nullable=False)
    strategy_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("strategy_runs.id"), nullable=False)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    timeframe: Mapped[str] = mapped_column(String(32), nullable=False)
    signal_type: Mapped[str] = mapped_column(String(32), nullable=False)
    signal_side: Mapped[str] = mapped_column(String(32), nullable=False)
    confidence_score: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    strength_score: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    generated_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)

    order_requests: Mapped[list["OrderRequest"]] = relationship(back_populates="signal_event")


class OrderRequest(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "order_requests"
    __table_args__ = (Index("ix_order_requests_run_requested_at", "strategy_run_id", "requested_at"),)

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    strategy_config_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("strategy_configs.id"), nullable=False)
    strategy_run_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("strategy_runs.id"), nullable=False)
    signal_event_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("signal_events.id"))
    requested_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    client_request_id: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=OrderRequestStatus.PENDING.value)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    order_type: Mapped[str] = mapped_column(String(16), nullable=False)
    time_in_force: Mapped[str] = mapped_column(String(16), nullable=False, default=TimeInForce.GTC.value)
    volume: Mapped[Decimal] = mapped_column(VOLUME_NUMERIC, nullable=False)
    limit_price: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    stop_price: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    stop_loss: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    take_profit: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    comment: Mapped[str | None] = mapped_column(String(255), nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    requested_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)

    signal_event: Mapped[SignalEvent | None] = relationship(back_populates="order_requests")
    order_result: Mapped["OrderResult | None"] = relationship(back_populates="order_request", uselist=False)


class OrderResult(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "order_results"
    __table_args__ = (
        UniqueConstraint("order_request_id", name="uq_order_results_order_request_id"),
        Index("ix_order_results_broker_order_id", "broker_order_id"),
    )

    order_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("order_requests.id"), nullable=False)
    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=OrderResultStatus.ACCEPTED.value)
    retcode: Mapped[str | None] = mapped_column(String(32), nullable=True)
    broker_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    broker_position_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    accepted_volume: Mapped[Decimal | None] = mapped_column(VOLUME_NUMERIC, nullable=True)
    accepted_price: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_payload: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    received_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)

    order_request: Mapped[OrderRequest] = relationship(back_populates="order_result")
    executions: Mapped[list["Execution"]] = relationship(back_populates="order_result")


class Execution(UUIDPrimaryKeyMixin, CreatedTimestampMixin, Base):
    __tablename__ = "executions"
    __table_args__ = (
        UniqueConstraint("deployment_id", "broker_execution_id", name="uq_executions_deployment_broker_execution"),
    )

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    order_request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("order_requests.id"))
    order_result_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("order_results.id"))
    broker_execution_id: Mapped[str] = mapped_column(String(64), nullable=False)
    broker_order_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    broker_position_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    volume: Mapped[Decimal] = mapped_column(VOLUME_NUMERIC, nullable=False)
    price: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)

    order_result: Mapped[OrderResult | None] = relationship(back_populates="executions")


class PositionSnapshot(UUIDPrimaryKeyMixin, CreatedTimestampMixin, Base):
    __tablename__ = "position_snapshots"
    __table_args__ = (Index("ix_position_snapshots_deployment_observed_at", "deployment_id", "observed_at"),)

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    broker_position_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    symbol: Mapped[str] = mapped_column(String(32), nullable=False)
    side: Mapped[str] = mapped_column(String(16), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default=PositionStatus.OPEN.value)
    volume: Mapped[Decimal] = mapped_column(VOLUME_NUMERIC, nullable=False)
    entry_price: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    mark_price: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    stop_loss: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    take_profit: Mapped[Decimal | None] = mapped_column(PRICE_NUMERIC, nullable=True)
    observed_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)


class AccountSnapshot(UUIDPrimaryKeyMixin, CreatedTimestampMixin, Base):
    __tablename__ = "account_snapshots"
    __table_args__ = (Index("ix_account_snapshots_deployment_observed_at", "deployment_id", "observed_at"),)

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    account_login: Mapped[str | None] = mapped_column(String(64), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    balance: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    equity: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    margin: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    free_margin: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    profit: Mapped[Decimal] = mapped_column(PRICE_NUMERIC, nullable=False)
    observed_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
