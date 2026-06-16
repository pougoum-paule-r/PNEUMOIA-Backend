"""add_soft_delete_patient

Revision ID: b2c3d4e5f6a7
Revises: 9487a644c3b9
Create Date: 2026-06-06 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = '9487a644c3b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP"))
    conn.execute(sa.text(
        "ALTER TABLE patients ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(15) "
        "REFERENCES medecins(id) ON DELETE SET NULL"
    ))


def downgrade() -> None:
    op.drop_column('patients', 'deleted_by')
    op.drop_column('patients', 'deleted_at')
