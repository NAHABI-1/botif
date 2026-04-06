from __future__ import annotations

from sqlalchemy.orm import Session

from mt5_platform_db.db.session import SessionLocal
from mt5_platform_db.models.identity import Role, User


def seed_roles(session: Session) -> None:
    existing = {role.code for role in session.query(Role).all()}
    for code, name in [("admin", "Admin"), ("operator", "Operator"), ("viewer", "Viewer")]:
        if code in existing:
            continue
        session.add(Role(code=code, name=name, description=f"{name} role"))


def seed_users(session: Session) -> None:
    if session.query(User).count() > 0:
        return
    session.add(
        User(
            email="demo-admin@example.com",
            display_name="Demo Admin",
            password_hash="demo-only",
            is_active=True,
        )
    )


def main() -> None:
    session = SessionLocal()
    try:
        seed_roles(session)
        seed_users(session)
        session.commit()
    finally:
        session.close()


if __name__ == "__main__":
    main()
