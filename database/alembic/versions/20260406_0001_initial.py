from __future__ import annotations

from alembic import op

revision = "20260406_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Schema managed by SQLAlchemy metadata; use autogenerate in real deployments.
    pass


def downgrade() -> None:
    pass
