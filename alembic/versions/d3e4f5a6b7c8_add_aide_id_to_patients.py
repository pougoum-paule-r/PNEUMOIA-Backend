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
    op.add_column('patients',
        sa.Column('aide_id', sa.String(15),
                  sa.ForeignKey('aides_soignants.id', ondelete='SET NULL'),
                  nullable=True)
    )


def downgrade() -> None:
    op.drop_column('patients', 'aide_id')
