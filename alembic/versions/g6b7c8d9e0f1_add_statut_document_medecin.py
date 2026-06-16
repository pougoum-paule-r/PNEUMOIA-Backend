"""add statut and motif_rejet to documents_medecin

Revision ID: g6b7c8d9e0f1
Revises: f5a6b7c8d9e0
Create Date: 2026-06-15 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa

revision = 'g6b7c8d9e0f1'
down_revision = 'f5a6b7c8d9e0'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""
        ALTER TABLE documents_medecin
        ADD COLUMN IF NOT EXISTS statut VARCHAR(20) NOT NULL DEFAULT 'en_attente'
    """)
    op.execute("""
        ALTER TABLE documents_medecin
        ADD COLUMN IF NOT EXISTS motif_rejet VARCHAR(500)
    """)


def downgrade() -> None:
    op.execute("ALTER TABLE documents_medecin DROP COLUMN IF EXISTS motif_rejet")
    op.execute("ALTER TABLE documents_medecin DROP COLUMN IF EXISTS statut")
