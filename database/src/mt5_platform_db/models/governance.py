from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mt5_platform_db.db.base import Base, CreatedTimestampMixin, UUIDPrimaryKeyMixin, UpdatedTimestampMixin, utc_now
from mt5_platform_db.db.enums import AlertStatus, RiskCategory, RiskSeverity
from mt5_platform_db.db.types import JSON_DOCUMENT


class RiskEvent(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "risk_events"
    __table_args__ = (
        Index("ix_risk_events_deployment_severity_occurred_at", "deployment_id", "severity", "occurred_at"),
    )

    deployment_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("deployments.id"), nullable=False)
    strategy_run_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("strategy_runs.id"))
    order_request_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("order_requests.id"))
    severity: Mapped[str] = mapped_column(String(16), nullable=False, default=RiskSeverity.WARNING.value)
    category: Mapped[str] = mapped_column(String(16), nullable=False, default=RiskCategory.RISK.value)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
    acknowledged_at: Mapped[datetime | None] = mapped_column(nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(nullable=True)

    alerts: Mapped[list["Alert"]] = relationship(back_populates="risk_event")


class Alert(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "alerts"
    __table_args__ = (Index("ix_alerts_status_created_at", "status", "created_at"),)

    risk_event_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("risk_events.id"))
    deployment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("deployments.id"))
    channel: Mapped[str] = mapped_column(String(32), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default=AlertStatus.PENDING.value)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    destination: Mapped[str] = mapped_column(String(255), nullable=False)
    dedupe_key: Mapped[str | None] = mapped_column(String(128), nullable=True, unique=True)
    attempt_count: Mapped[int] = mapped_column(default=0)
    last_attempt_at: Mapped[datetime | None] = mapped_column(nullable=True)
    sent_at: Mapped[datetime | None] = mapped_column(nullable=True)
    acknowledged_at: Mapped[datetime | None] = mapped_column(nullable=True)
    alert_metadata: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)

    risk_event: Mapped[RiskEvent | None] = relationship(back_populates="alerts")


class AuditLog(UUIDPrimaryKeyMixin, CreatedTimestampMixin, Base):
    __tablename__ = "audit_logs"
    __table_args__ = (Index("ix_audit_logs_entity_occurred_at", "entity_type", "entity_id", "occurred_at"),)

    actor_user_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    actor_type: Mapped[str] = mapped_column(String(32), nullable=False)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(64), nullable=False)
    entity_id: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    deployment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("deployments.id"))
    request_id: Mapped[str | None] = mapped_column(String(64))
    ip_address: Mapped[str | None] = mapped_column(String(64))
    changes: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    audit_metadata: Mapped[dict[str, object]] = mapped_column(JSON_DOCUMENT, nullable=False, default=dict)
    occurred_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
