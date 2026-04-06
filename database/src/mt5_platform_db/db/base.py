from __future__ import annotations

from datetime import datetime, timezone
import re
import uuid

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

DATABASE_SCHEMA = "trading"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def validate_schema_identifier(value: str) -> str:
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", value):
        raise ValueError("Invalid schema identifier.")
    return value


class Base(DeclarativeBase):
    metadata = MetaData(schema=DATABASE_SCHEMA)


class UUIDPrimaryKeyMixin:
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)


class CreatedTimestampMixin:
    created_at: Mapped[datetime] = mapped_column(default=utc_now)


class UpdatedTimestampMixin:
    updated_at: Mapped[datetime] = mapped_column(default=utc_now, onupdate=utc_now)
