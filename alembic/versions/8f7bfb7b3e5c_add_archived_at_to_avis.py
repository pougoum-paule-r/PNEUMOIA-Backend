"""add_archived_at_to_avis

Revision ID: 8f7bfb7b3e5c
Revises: a0b1c2d3e4f5
Create Date: 2026-06-26 20:49:18.313051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '8f7bfb7b3e5c'
down_revision: Union[str, None] = 'a0b1c2d3e4f5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('avis', sa.Column('archived_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('avis', 'archived_at')
