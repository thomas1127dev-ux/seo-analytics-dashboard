"""ensure alembic_version.version_num is varchar(64)

Alembic creates alembic_version with version_num VARCHAR(32) when the table
is first created. Our revision IDs (e.g. 0003_add_user_and_permission_tables)
exceed 32 chars, causing "Data too long for column 'version_num'".
This migration runs first and widens the column to 64 before any long IDs are written.

Revision ID: 0000_alembic_version_64
Revises:
Create Date: 2026-03-12

"""

from __future__ import annotations

from alembic import op


revision = "0000_alembic_version_64"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alembic has already created alembic_version with version_num VARCHAR(32).
    # Widen to 64 so long revision IDs (e.g. 0003_add_user_and_permission_tables) fit.
    op.execute("ALTER TABLE alembic_version MODIFY version_num VARCHAR(64) NOT NULL")


def downgrade() -> None:
    op.execute("ALTER TABLE alembic_version MODIFY version_num VARCHAR(32) NOT NULL")
