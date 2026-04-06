from __future__ import annotations

import uuid

from sqlalchemy import select

from mt5_platform_db.models.trading import (
    AccountSnapshot,
    Execution,
    OrderRequest,
    OrderResult,
    PositionSnapshot,
    SignalEvent,
)
from mt5_platform_db.repositories.base import SQLAlchemyRepository


class SignalEventRepository(SQLAlchemyRepository[SignalEvent]):
    model = SignalEvent

    def list_for_run(self, strategy_run_id: uuid.UUID, *, limit: int = 100) -> list[SignalEvent]:
        stmt = select(SignalEvent).where(SignalEvent.strategy_run_id == strategy_run_id).limit(limit)
        return list(self.session.scalars(stmt))


class OrderRequestRepository(SQLAlchemyRepository[OrderRequest]):
    model = OrderRequest

    def list_for_run(self, strategy_run_id: uuid.UUID, *, limit: int = 100) -> list[OrderRequest]:
        stmt = select(OrderRequest).where(OrderRequest.strategy_run_id == strategy_run_id).limit(limit)
        return list(self.session.scalars(stmt))


class OrderResultRepository(SQLAlchemyRepository[OrderResult]):
    model = OrderResult

    def get_by_request_id(self, order_request_id: uuid.UUID) -> OrderResult | None:
        stmt = select(OrderResult).where(OrderResult.order_request_id == order_request_id)
        return self.session.scalar(stmt)


class ExecutionRepository(SQLAlchemyRepository[Execution]):
    model = Execution

    def list_recent(self, *, limit: int = 100) -> list[Execution]:
        stmt = select(Execution).limit(limit)
        return list(self.session.scalars(stmt))


class PositionSnapshotRepository(SQLAlchemyRepository[PositionSnapshot]):
    model = PositionSnapshot

    def list_recent(self, *, limit: int = 100) -> list[PositionSnapshot]:
        stmt = select(PositionSnapshot).limit(limit)
        return list(self.session.scalars(stmt))


class AccountSnapshotRepository(SQLAlchemyRepository[AccountSnapshot]):
    model = AccountSnapshot

    def list_recent(self, *, limit: int = 100) -> list[AccountSnapshot]:
        stmt = select(AccountSnapshot).limit(limit)
        return list(self.session.scalars(stmt))
