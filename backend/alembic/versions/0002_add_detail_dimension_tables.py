"""add detail dimension tables

Revision ID: 0002_add_detail_dimension_tables
Revises: 0001_init_core_tables
Create Date: 2026-03-10

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_add_detail_dimension_tables"
down_revision = "0001_init_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "ga4_channel_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("channel", sa.String(length=64), nullable=False),
        sa.Column("sessions", sa.Integer(), nullable=True),
        sa.Column("users", sa.Integer(), nullable=True),
        sa.Column("page_views", sa.Integer(), nullable=True),
        sa.UniqueConstraint(
            "project_id",
            "date",
            "channel",
            name="uq_ga4_channel_project_date_channel",
        ),
    )
    op.create_index(
        "ix_ga4_channel_daily_project_id", "ga4_channel_daily", ["project_id"]
    )
    op.create_index("ix_ga4_channel_daily_date", "ga4_channel_daily", ["date"])
    op.create_index("ix_ga4_channel_daily_channel", "ga4_channel_daily", ["channel"])

    op.create_table(
        "ga4_page_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("page_path", sa.String(length=512), nullable=False),
        sa.Column("page_views", sa.Integer(), nullable=True),
        sa.Column("avg_engagement_time", sa.Float(), nullable=True),
        sa.Column("bounce_rate", sa.Float(), nullable=True),
        sa.UniqueConstraint(
            "project_id",
            "date",
            "page_path",
            name="uq_ga4_page_project_date_path",
        ),
    )
    op.create_index("ix_ga4_page_daily_project_id", "ga4_page_daily", ["project_id"])
    op.create_index("ix_ga4_page_daily_date", "ga4_page_daily", ["date"])
    op.create_index("ix_ga4_page_daily_page_path", "ga4_page_daily", ["page_path"])

    op.create_table(
        "gsc_query_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("query", sa.String(length=512), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("ctr", sa.Float(), nullable=True),
        sa.Column("avg_position", sa.Float(), nullable=True),
        sa.UniqueConstraint(
            "project_id", "date", "query", name="uq_gsc_query_project_date_query"
        ),
    )
    op.create_index("ix_gsc_query_daily_project_id", "gsc_query_daily", ["project_id"])
    op.create_index("ix_gsc_query_daily_date", "gsc_query_daily", ["date"])
    op.create_index("ix_gsc_query_daily_query", "gsc_query_daily", ["query"])

    op.create_table(
        "gsc_page_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("page", sa.String(length=512), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("ctr", sa.Float(), nullable=True),
        sa.Column("avg_position", sa.Float(), nullable=True),
        sa.UniqueConstraint(
            "project_id", "date", "page", name="uq_gsc_page_project_date_page"
        ),
    )
    op.create_index("ix_gsc_page_daily_project_id", "gsc_page_daily", ["project_id"])
    op.create_index("ix_gsc_page_daily_date", "gsc_page_daily", ["date"])
    op.create_index("ix_gsc_page_daily_page", "gsc_page_daily", ["page"])

    op.create_table(
        "yandex_query_daily",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("query", sa.String(length=512), nullable=False),
        sa.Column("impressions", sa.Integer(), nullable=True),
        sa.Column("clicks", sa.Integer(), nullable=True),
        sa.Column("ctr", sa.Float(), nullable=True),
        sa.UniqueConstraint(
            "project_id", "date", "query", name="uq_yandex_query_project_date_query"
        ),
    )
    op.create_index(
        "ix_yandex_query_daily_project_id", "yandex_query_daily", ["project_id"]
    )
    op.create_index("ix_yandex_query_daily_date", "yandex_query_daily", ["date"])
    op.create_index("ix_yandex_query_daily_query", "yandex_query_daily", ["query"])


def downgrade() -> None:
    op.drop_index("ix_yandex_query_daily_query", table_name="yandex_query_daily")
    op.drop_index("ix_yandex_query_daily_date", table_name="yandex_query_daily")
    op.drop_index(
        "ix_yandex_query_daily_project_id", table_name="yandex_query_daily"
    )
    op.drop_table("yandex_query_daily")

    op.drop_index("ix_gsc_page_daily_page", table_name="gsc_page_daily")
    op.drop_index("ix_gsc_page_daily_date", table_name="gsc_page_daily")
    op.drop_index("ix_gsc_page_daily_project_id", table_name="gsc_page_daily")
    op.drop_table("gsc_page_daily")

    op.drop_index("ix_gsc_query_daily_query", table_name="gsc_query_daily")
    op.drop_index("ix_gsc_query_daily_date", table_name="gsc_query_daily")
    op.drop_index("ix_gsc_query_daily_project_id", table_name="gsc_query_daily")
    op.drop_table("gsc_query_daily")

    op.drop_index("ix_ga4_page_daily_page_path", table_name="ga4_page_daily")
    op.drop_index("ix_ga4_page_daily_date", table_name="ga4_page_daily")
    op.drop_index("ix_ga4_page_daily_project_id", table_name="ga4_page_daily")
    op.drop_table("ga4_page_daily")

    op.drop_index("ix_ga4_channel_daily_channel", table_name="ga4_channel_daily")
    op.drop_index("ix_ga4_channel_daily_date", table_name="ga4_channel_daily")
    op.drop_index(
        "ix_ga4_channel_daily_project_id", table_name="ga4_channel_daily"
    )
    op.drop_table("ga4_channel_daily")

