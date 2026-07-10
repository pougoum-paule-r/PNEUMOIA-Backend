"""add corbeille to statut_medecin enum

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-06-15 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op


revision: str = 'e4f5a6b7c8d9'
down_revision: Union[str, None] = 'd3e4f5a6b7c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE statut_medecin ADD VALUE IF NOT EXISTS 'corbeille'")


def downgrade() -> None:
    # PostgreSQL ne permet pas de retirer une valeur d'enum sans recréer le type
    pass
