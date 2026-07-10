"""add created_by_aide to patients

Revision ID: i8d9e0f1a2b3
Revises: h7c8d9e0f1a2
Create Date: 2026-06-18 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'i8d9e0f1a2b3'
down_revision: Union[str, None] = 'h7c8d9e0f1a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.get_bind().execute(sa.text(
        "ALTER TABLE patients ADD COLUMN IF NOT EXISTS created_by_aide VARCHAR(15) "
        "REFERENCES aides_soignants(id) ON DELETE SET NULL"
    ))
    op.get_bind().execute(sa.text(
        "CREATE INDEX IF NOT EXISTS idx_patients_aide ON patients(created_by_aide)"
    ))


def downgrade() -> None:
    op.drop_index('idx_patients_aide', table_name='patients')
    op.drop_column('patients', 'created_by_aide')
