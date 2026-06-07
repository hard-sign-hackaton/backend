"""remove template columns

Revision ID: 20260607_0002
Revises: 20260606_0001
Create Date: 2026-06-07
"""

from alembic import op
import sqlalchemy as sa

revision = "20260607_0002"
down_revision = "20260606_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove legacy template columns — front-end provides all template data via `layout` JSONB
    with op.batch_alter_table("templates") as batch_op:
        # Safe to drop if present in schema
        try:
            batch_op.drop_column("title")
        except Exception:
            pass
        try:
            batch_op.drop_column("theme")
        except Exception:
            pass
        try:
            batch_op.drop_column("grid_columns")
        except Exception:
            pass
        try:
            batch_op.drop_column("background_url")
        except Exception:
            pass


def downgrade() -> None:
    # Recreate legacy columns as nullable to avoid data loss during downgrade.
    with op.batch_alter_table("templates") as batch_op:
        batch_op.add_column(sa.Column("title", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("theme", sa.String(), nullable=True))
        batch_op.add_column(sa.Column("grid_columns", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("background_url", sa.String(), nullable=True))
