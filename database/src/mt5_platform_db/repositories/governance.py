from __future__ import annotations

from sqlalchemy import select

from mt5_platform_db.models.governance import Alert, AuditLog, RiskEvent
from mt5_platform_db.repositories.base import SQLAlchemyRepository


class RiskEventRepository(SQLAlchemyRepository[RiskEvent]):
    model = RiskEvent

    def list_recent(self, *, limit: int = 100) -> list[RiskEvent]:
        stmt = select(RiskEvent).limit(limit)
        return list(self.session.scalars(stmt))


class AlertRepository(SQLAlchemyRepository[Alert]):
    model = Alert

    def list_recent(self, *, limit: int = 100) -> list[Alert]:
        stmt = select(Alert).limit(limit)
        return list(self.session.scalars(stmt))


class AuditLogRepository(SQLAlchemyRepository[AuditLog]):
    model = AuditLog

    def list_recent(self, *, limit: int = 100) -> list[AuditLog]:
        stmt = select(AuditLog).limit(limit)
        return list(self.session.scalars(stmt))
