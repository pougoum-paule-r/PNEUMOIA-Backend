"""add_statut_to_avis

Revision ID: j9e0f1a2b3c4
Revises: 75c4fafbcb84
Create Date: 2026-06-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'j9e0f1a2b3c4'
down_revision: Union[str, None] = '75c4fafbcb84'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'avis',
        sa.Column('statut', sa.String(length=20), nullable=False, server_default='publie'),
    )


def downgrade() -> None:
    op.drop_column('avis', 'statut')
