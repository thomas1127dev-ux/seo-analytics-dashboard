"""add ga4 retention and user metrics

Revision ID: 0004_add_ga4_retention_metrics
Revises: 0003_add_user_and_permission_tables
Create Date: 2026-03-12

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_add_ga4_retention_metrics"
down_revision = "0003_add_user_and_permission_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ga4_daily", sa.Column("new_users", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("returning_users", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("retention_d1", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("retention_d3", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("retention_d7", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("ga4_daily", "retention_d7")
    op.drop_column("ga4_daily", "retention_d3")
    op.drop_column("ga4_daily", "retention_d1")
    op.drop_column("ga4_daily", "returning_users")
    op.drop_column("ga4_daily", "new_users")

