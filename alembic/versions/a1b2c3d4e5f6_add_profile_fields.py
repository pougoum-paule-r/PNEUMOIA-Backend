"""add profile fields to medecins

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-05-29

"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('medecins', sa.Column('telephone', sa.String(30),  nullable=True))
    op.add_column('medecins', sa.Column('adresse',   sa.String(300), nullable=True))
    op.add_column('medecins', sa.Column('bio',       sa.Text(),      nullable=True))
    op.add_column('medecins ', sa.Column('linkedin',  sa.String(300), nullable=True))
    op.add_column('medecins', sa.Column('website',   sa.String(300), nullable=True))


def downgrade() -> None:
    op.drop_column('medecins', 'website')
    op.drop_column('medecins', 'linkedin')
    op.drop_column('medecins', 'bio')
    op.drop_column('medecins', 'adresse')
    op.drop_column('medecins', 'telephone')
