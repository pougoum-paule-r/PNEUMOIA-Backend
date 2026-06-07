"""add statut_clinique

Revision ID: b1adbd9ba7bb
Revises: b2c3d4e5f6a7
Create Date: 2026-06-07 00:40:42.773996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1adbd9ba7bb'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


statut_clinique_enum = sa.Enum(
    'stable', 'surveille', 'urgent', 'critique',
    name='statut_clinique_enum',
)


def upgrade() -> None:
    statut_clinique_enum.create(op.get_bind(), checkfirst=True)
    op.add_column(
        'consultations',
        sa.Column('statut_clinique', statut_clinique_enum, nullable=True),
    )


def downgrade() -> None:
    op.drop_column('consultations', 'statut_clinique')
    statut_clinique_enum.drop(op.get_bind(), checkfirst=True)
