from __future__ import annotations

from datetime import datetime
import uuid

from sqlalchemy import Boolean, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mt5_platform_db.db.base import Base, CreatedTimestampMixin, UUIDPrimaryKeyMixin, UpdatedTimestampMixin, utc_now
from mt5_platform_db.db.enums import SessionStatus


class Role(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    system_defined: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))

    user_links: Mapped[list["UserRole"]] = relationship(back_populates="role", cascade="all, delete-orphan")


class User(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (Index("ix_users_active_created_at", "is_active", "created_at"),)

    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    display_name: Mapped[str] = mapped_column(String(128), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    is_service_account: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"))
    last_login_at: Mapped[datetime | None] = mapped_column(nullable=True)

    role_links: Mapped[list["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    sessions: Mapped[list["SessionRecord"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserRole(CreatedTimestampMixin, Base):
    __tablename__ = "user_roles"
    __table_args__ = (Index("ix_user_roles_role_id", "role_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    role_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)

    user: Mapped[User] = relationship(back_populates="role_links")
    role: Mapped[Role] = relationship(back_populates="user_links")


class SessionRecord(UUIDPrimaryKeyMixin, UpdatedTimestampMixin, Base):
    __tablename__ = "sessions"
    __table_args__ = (Index("ix_sessions_user_status_expires_at", "user_id", "status", "expires_at"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    status: Mapped[SessionStatus] = mapped_column(String(32), nullable=False, default=SessionStatus.ACTIVE.value)
    ip_address: Mapped[str | None] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    issued_at: Mapped[datetime] = mapped_column(nullable=False, default=utc_now)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(nullable=True)
    last_seen_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")
