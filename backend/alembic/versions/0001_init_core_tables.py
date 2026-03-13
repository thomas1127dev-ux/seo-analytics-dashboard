"""init core tables

Revision ID: 0001_init_core_tables
Revises:
Create Date: 2026-03-10

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_init_core_tables"
down_revision = "0000_alembic_version_64"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_key", sa.String(length=64), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("domain", sa.String(length=255), nullable=False),
        sa.Column("ga4_property_id", sa.String(length=64), nullable=True),
        sa.Column("gsc_property", sa.String(length=255), nullable=True),
        sa.Column("yandex_host", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("project_key", name="uq_projects_project_key"),
    )
    op.create_index("ix_projects_project_key", "projects", ["project_key"])

    op.create_table(
        "ga4_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("dau", sa.Integer(), nullable=True),
        sa.Column("sessions", sa.Integer(), nullable=True),
        sa.Column("page_views", sa.Integer(), nullable=True),
        sa.Column("avg_engagement_time", sa.Float(), nullable=True),
        sa.Column("engagement_rate", sa.Float(), nullable=True),
        sa.Column("bounce_rate", sa.Float(), nullable=True),
        sa.UniqueConstraint("project_id", "date", name="uq_ga4_daily_project_date"),
    )
    op.create_index("ix_ga4_daily_project_id", "ga4_daily", ["project_id"])
    op.create_index("ix_ga4_daily_date", "ga4_daily", ["date"])

    op.create_table(
        "gsc_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("ctr", sa.Float(), nullable=True),
        sa.Column("avg_position", sa.Float(), nullable=True),
        sa.UniqueConstraint("project_id", "date", name="uq_gsc_daily_project_date"),
    )
    op.create_index("ix_gsc_daily_project_id", "gsc_daily", ["project_id"])
    op.create_index("ix_gsc_daily_date", "gsc_daily", ["date"])

    op.create_table(
        "yandex_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("ctr", sa.Float(), nullable=True),
        sa.Column("avg_position", sa.Float(), nullable=True),
        sa.UniqueConstraint("project_id", "date", name="uq_yandex_daily_project_date"),
    )
    op.create_index("ix_yandex_daily_project_id", "yandex_daily", ["project_id"])
    op.create_index("ix_yandex_daily_date", "yandex_daily", ["date"])


def downgrade() -> None:
    op.drop_index("ix_yandex_daily_date", table_name="yandex_daily")
    op.drop_index("ix_yandex_daily_project_id", table_name="yandex_daily")
    op.drop_table("yandex_daily")

    op.drop_index("ix_gsc_daily_date", table_name="gsc_daily")
    op.drop_index("ix_gsc_daily_project_id", table_name="gsc_daily")
    op.drop_table("gsc_daily")

    op.drop_index("ix_ga4_daily_date", table_name="ga4_daily")
    op.drop_index("ix_ga4_daily_project_id", table_name="ga4_daily")
    op.drop_table("ga4_daily")

    op.drop_index("ix_projects_project_key", table_name="projects")
    op.drop_table("projects")

