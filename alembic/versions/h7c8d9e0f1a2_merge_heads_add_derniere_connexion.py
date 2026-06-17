"""merge heads and add derniere_connexion to medecins

Revision ID: h7c8d9e0f1a2
Revises: 3c6cb56caf02, 75c4fafbcb84
Create Date: 2026-06-17 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'h7c8d9e0f1a2'
down_revision: Union[str, tuple] = ('3c6cb56caf02', '75c4fafbcb84')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'medecins',
        sa.Column('derniere_connexion', sa.DateTime(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('medecins', 'derniere_connexion')
