from __future__ import annotations

import uuid

from sqlalchemy import select

from mt5_platform_db.models.identity import Role, SessionRecord, User
from mt5_platform_db.repositories.base import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.session.scalar(stmt)


class RoleRepository(SQLAlchemyRepository[Role]):
    model = Role

    def get_by_code(self, code: str) -> Role | None:
        stmt = select(Role).where(Role.code == code)
        return self.session.scalar(stmt)


class SessionRepository(SQLAlchemyRepository[SessionRecord]):
    model = SessionRecord

    def list_active_for_user(self, user_id: uuid.UUID, *, limit: int = 20) -> list[SessionRecord]:
        stmt = select(SessionRecord).where(SessionRecord.user_id == user_id).limit(limit)
        return list(self.session.scalars(stmt))
