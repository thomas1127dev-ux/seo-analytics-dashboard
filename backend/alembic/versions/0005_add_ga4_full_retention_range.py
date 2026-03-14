"""add full 1-7 day retention columns for ga4_daily

Revision ID: 0005_add_ga4_full_retention_range
Revises: 0004_add_ga4_retention_metrics
Create Date: 2026-03-12

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_add_ga4_full_retention_range"
down_revision = "0004_add_ga4_retention_metrics"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("ga4_daily", sa.Column("retention_d2", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("retention_d4", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("retention_d5", sa.Integer(), nullable=True))
    op.add_column("ga4_daily", sa.Column("retention_d6", sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column("ga4_daily", "retention_d6")
    op.drop_column("ga4_daily", "retention_d5")
    op.drop_column("ga4_daily", "retention_d4")
    op.drop_column("ga4_daily", "retention_d2")

