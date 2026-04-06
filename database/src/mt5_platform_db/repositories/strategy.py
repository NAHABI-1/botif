from __future__ import annotations

import uuid

from sqlalchemy import select

from mt5_platform_db.models.strategy import Deployment, StrategyConfig, StrategyRun
from mt5_platform_db.repositories.base import SQLAlchemyRepository


class StrategyConfigRepository(SQLAlchemyRepository[StrategyConfig]):
    model = StrategyConfig

    def get_by_slug_version(self, slug: str, version: int) -> StrategyConfig | None:
        stmt = select(StrategyConfig).where(StrategyConfig.slug == slug, StrategyConfig.version == version)
        return self.session.scalar(stmt)


class DeploymentRepository(SQLAlchemyRepository[Deployment]):
    model = Deployment

    def get_by_name(self, name: str) -> Deployment | None:
        stmt = select(Deployment).where(Deployment.name == name)
        return self.session.scalar(stmt)


class StrategyRunRepository(SQLAlchemyRepository[StrategyRun]):
    model = StrategyRun

    def list_recent_for_deployment(self, deployment_id: uuid.UUID, *, limit: int = 50) -> list[StrategyRun]:
        stmt = select(StrategyRun).where(StrategyRun.deployment_id == deployment_id).limit(limit)
        return list(self.session.scalars(stmt))
