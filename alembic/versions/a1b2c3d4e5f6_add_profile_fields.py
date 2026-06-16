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
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS telephone VARCHAR(30)"))
    conn.execute(sa.text("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS adresse VARCHAR(300)"))
    conn.execute(sa.text("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS bio TEXT"))
    conn.execute(sa.text("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS linkedin VARCHAR(300)"))
    conn.execute(sa.text("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS website VARCHAR(300)"))


def downgrade() -> None:
    op.drop_column('medecins', 'website')
    op.drop_column('medecins', 'linkedin')
    op.drop_column('medecins', 'bio')
    op.drop_column('medecins', 'adresse')
    op.drop_column('medecins', 'telephone')
