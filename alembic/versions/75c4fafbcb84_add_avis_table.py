"""add_avis_table

Revision ID: 75c4fafbcb84
Revises: 23ce3c55b54a
Create Date: 2026-06-16 21:46:50.870626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '75c4fafbcb84'
down_revision: Union[str, None] = '23ce3c55b54a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'avis',
        sa.Column('id',            sa.String(length=15),  nullable=False),
        sa.Column('medecin_id',    sa.String(length=15),  nullable=False),
        sa.Column('prenom',        sa.String(length=100), nullable=False),
        sa.Column('nom',           sa.String(length=100), nullable=False),
        sa.Column('civilite',      sa.String(length=20),  nullable=True),
        sa.Column('specialite',    sa.String(length=150), nullable=True),
        sa.Column('etablissement', sa.String(length=200), nullable=True),
        sa.Column('ville',         sa.String(length=100), nullable=True),
        sa.Column('photo_url',     sa.String(length=500), nullable=True),
        sa.Column('note',          sa.Integer(),          nullable=False),
        sa.Column('commentaire',   sa.Text(),             nullable=False),
        sa.Column('vu',            sa.Boolean(),          nullable=False),
        sa.Column('created_at',    sa.DateTime(),         nullable=False),
        sa.ForeignKeyConstraint(['medecin_id'], ['medecins.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('avis')
