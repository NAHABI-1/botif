from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from mt5_platform_db.settings import settings

engine = create_engine(settings.database_url, echo=settings.database_echo, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
