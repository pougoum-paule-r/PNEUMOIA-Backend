"""add_ville_to_medecins

Revision ID: 33368a2467f1
Revises: g6b7c8d9e0f1
Create Date: 2026-06-15 22:23:16.942312

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '33368a2467f1'
down_revision: Union[str, None] = 'g6b7c8d9e0f1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('medecins', sa.Column('ville', sa.String(length=100), nullable=True))


def downgrade() -> None:
    op.drop_column('medecins', 'ville')
