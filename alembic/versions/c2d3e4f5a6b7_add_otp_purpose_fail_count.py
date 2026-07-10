"""add purpose and fail_count to otp_codes

Revision ID: c2d3e4f5a6b7
Revises: b1adbd9ba7bb
Create Date: 2026-06-07 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, None] = 'b1adbd9ba7bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text(
        "ALTER TABLE otp_codes ADD COLUMN IF NOT EXISTS purpose VARCHAR(20) NOT NULL DEFAULT 'login'"
    ))
    conn.execute(sa.text(
        "ALTER TABLE otp_codes ADD COLUMN IF NOT EXISTS fail_count INTEGER NOT NULL DEFAULT 0"
    ))


def downgrade() -> None:
    op.drop_column('otp_codes', 'fail_count')
    op.drop_column('otp_codes', 'purpose')
