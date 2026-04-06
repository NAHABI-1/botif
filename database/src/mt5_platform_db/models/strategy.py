from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import Boolean, ForeignKey, Index, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mt5_platform_db.db.base import Base, UUIDPrimaryKeyMixin, UpdatedTimestampMixin
from mt5_platform_db.db.enums import StrategyRunStatus, TradingMode
from mt5_platform_db.db.types import JSON_DOCUMENT


class StrategyConfig(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "strategy_configs"
    __table_args__ = (
        UniqueConstraint("slug", "version", name="uq_strategy_configs_slug_version"),
        Index("ix_strategy_configs_status_updated_at", "status", "updated_at"),
    )

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    timeframe: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    symbols: Mapped[list[str]] = mapped_column(JSON_DOCUMENT, nullable=False, default=list)
    parameters: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    risk_limits: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    is_template: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    checksum: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    created_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    updated_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))

    runs: Mapped[list["StrategyRun"]] = relationship(back_populates="strategy_config")


class Deployment(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "deployments"
    __table_args__ = (Index("ix_deployments_status_environment", "status", "environment"),)

    name: Mapped[str] = mapped_column(String(128), nullable=False)
    environment: Mapped[str] = mapped_column(String(32), nullable=False, default="local")
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="planned")
    trading_mode: Mapped[str] = mapped_column(String(32), nullable=False, default=TradingMode.PAPER.value)
    service_name: Mapped[str] = mapped_column(String(128), nullable=False)
    release_version: Mapped[str | None] = mapped_column(String(64), nullable=True)
    artifact_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    broker_server: Mapped[str | None] = mapped_column(String(128), nullable=True)
    account_login: Mapped[str | None] = mapped_column(String(64), nullable=True)
    deployment_metadata: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(nullable=True)

    runs: Mapped[list["StrategyRun"]] = relationship(back_populates="deployment")


class StrategyRun(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "strategy_runs"
    __table_args__ = (Index("ix_strategy_runs_deployment_status_created_at", "deployment_id", "status", "created_at"),)

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    strategy_config_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("strategy_configs.id"), nullable=False)
    triggered_by_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=StrategyRunStatus.PENDING.value)
    run_mode: Mapped[str] = mapped_column(String(32), nullable=False, default=TradingMode.PAPER.value)
    run_label: Mapped[str | None] = mapped_column(String(128), nullable=True)
    summary: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    heartbeat_at: Mapped[datetime | None] = mapped_column(nullable=True)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    deployment: Mapped[Deployment] = relationship(back_populates="runs")
    strategy_config: Mapped[StrategyConfig] = relationship(back_populates="runs")
