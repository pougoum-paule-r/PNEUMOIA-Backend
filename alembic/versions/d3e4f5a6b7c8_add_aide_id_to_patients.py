"""add aide_id to patients

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-06-12 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'd3e4f5a6b7c8'
down_revision: Union[str, None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE patients ADD COLUMN IF NOT EXISTS aide_id VARCHAR(15) "
        "REFERENCES aides_soignants(id) ON DELETE SET NULL"
    ))


def downgrade() -> None:
    op.drop_column('patients', 'aide_id')
