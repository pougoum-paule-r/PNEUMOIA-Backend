"""add_avis_medecins_table

Revision ID: 3c6cb56caf02
Revises: 23ce3c55b54a
Create Date: 2026-06-17 07:01:05.064706

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c6cb56caf02'
down_revision: Union[str, None] = '23ce3c55b54a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # NOTE: les changements détectés sur 'commentaires' (parent_id, auteur_type,
    # auteur_aide_id, likes_count, nullabilité auteur_id) sont un chantier séparé
    # non lié à cette migration et ont été retirés volontairement.
    op.create_table(
        'avis_medecins',
        sa.Column('id',         sa.String(length=15),  nullable=False),
        sa.Column('medecin_id', sa.String(length=15),  nullable=False),
        sa.Column('note',       sa.Integer(),           nullable=False),
        sa.Column('contenu',    sa.Text(),              nullable=False),
        sa.Column('vu',         sa.Boolean(),           nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(),          nullable=False),
        sa.ForeignKeyConstraint(['medecin_id'], ['medecins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('avis_medecins')
