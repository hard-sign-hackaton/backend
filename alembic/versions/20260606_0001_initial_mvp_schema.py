"""initial MVP schema

Revision ID: 20260606_0001
Revises:
Create Date: 2026-06-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260606_0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("entity_id", sa.String(), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_created_at"), "audit_logs", ["created_at"], unique=False)

    op.create_table(
        "display_groups",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "displays",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("pairing_code", sa.String(), nullable=False),
        sa.Column("ujin_complex_id", sa.Integer(), nullable=False),
        sa.Column("ujin_building_id", sa.Integer(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_displays_pairing_code"), "displays", ["pairing_code"], unique=True)
    op.create_index(op.f("ix_displays_status"), "displays", ["status"], unique=False)
    op.create_index(op.f("ix_displays_ujin_building_id"), "displays", ["ujin_building_id"], unique=False)

    op.create_table(
        "emergency_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("reset_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_emergency_events_starts_at"), "emergency_events", ["starts_at"], unique=False)
    op.create_index(op.f("ix_emergency_events_status"), "emergency_events", ["status"], unique=False)

    op.create_table(
        "static_content",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("content_type", sa.String(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("media_url", sa.String(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_to", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("theme", sa.String(), nullable=False),
        sa.Column("grid_columns", sa.Integer(), nullable=False),
        sa.Column("background_url", sa.String(), nullable=True),
        sa.Column("layout", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "display_group_members",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_group_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["display_group_id"], ["display_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["display_id"], ["displays.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("display_group_id", "display_id", name="uq_display_group_member"),
    )
    op.create_index(op.f("ix_display_group_members_display_group_id"), "display_group_members", ["display_group_id"], unique=False)
    op.create_index(op.f("ix_display_group_members_display_id"), "display_group_members", ["display_id"], unique=False)

    op.create_table(
        "display_template_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["display_id"], ["displays.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_display_template_assignments_display_id"), "display_template_assignments", ["display_id"], unique=True)

    op.create_table(
        "emergency_targets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("emergency_event_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("display_group_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("target_type", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["display_group_id"], ["display_groups.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["display_id"], ["displays.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["emergency_event_id"], ["emergency_events.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("emergency_event_id", "display_id", "display_group_id", "target_type", name="uq_emergency_target"),
    )
    op.create_index(op.f("ix_emergency_targets_display_group_id"), "emergency_targets", ["display_group_id"], unique=False)
    op.create_index(op.f("ix_emergency_targets_display_id"), "emergency_targets", ["display_id"], unique=False)

    op.create_table(
        "template_widgets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("static_content_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("x", sa.Integer(), nullable=False),
        sa.Column("y", sa.Integer(), nullable=False),
        sa.Column("w", sa.Integer(), nullable=False),
        sa.Column("h", sa.Integer(), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["static_content_id"], ["static_content.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["template_id"], ["templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_template_widgets_template_id"), "template_widgets", ["template_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_template_widgets_template_id"), table_name="template_widgets")
    op.drop_table("template_widgets")

    op.drop_index(op.f("ix_emergency_targets_display_id"), table_name="emergency_targets")
    op.drop_index(op.f("ix_emergency_targets_display_group_id"), table_name="emergency_targets")
    op.drop_table("emergency_targets")

    op.drop_index(op.f("ix_display_template_assignments_display_id"), table_name="display_template_assignments")
    op.drop_table("display_template_assignments")

    op.drop_index(op.f("ix_display_group_members_display_id"), table_name="display_group_members")
    op.drop_index(op.f("ix_display_group_members_display_group_id"), table_name="display_group_members")
    op.drop_table("display_group_members")

    op.drop_table("templates")
    op.drop_table("static_content")

    op.drop_index(op.f("ix_emergency_events_status"), table_name="emergency_events")
    op.drop_index(op.f("ix_emergency_events_starts_at"), table_name="emergency_events")
    op.drop_table("emergency_events")

    op.drop_index(op.f("ix_displays_ujin_building_id"), table_name="displays")
    op.drop_index(op.f("ix_displays_status"), table_name="displays")
    op.drop_index(op.f("ix_displays_pairing_code"), table_name="displays")
    op.drop_table("displays")

    op.drop_table("display_groups")

    op.drop_index(op.f("ix_audit_logs_created_at"), table_name="audit_logs")
    op.drop_table("audit_logs")
