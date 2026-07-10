"""add_patient_fields

Revision ID: 9487a644c3b9
Revises: a1b2c3d4e5f6
Create Date: 2026-05-30 11:01:36.507674

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '9487a644c3b9'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("ALTER TABLE consultations ADD COLUMN IF NOT EXISTS antecedents_consultation JSONB"))
    conn.execute(sa.text("ALTER TABLE consultations ADD COLUMN IF NOT EXISTS observations TEXT"))
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS civilite VARCHAR(10)"))
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS adresse VARCHAR(300)"))
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS profession VARCHAR(150)"))
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS personne_a_contacter VARCHAR(150)"))
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS telephone_urgence VARCHAR(20)"))
    conn.execute(sa.text("ALTER TABLE patients ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP"))


def downgrade() -> None:
    op.drop_column('patients', 'updated_at')
    op.drop_column('patients', 'telephone_urgence')
    op.drop_column('patients', 'personne_a_contacter')
    op.drop_column('patients', 'profession')
    op.drop_column('patients', 'adresse')
    op.drop_column('patients', 'civilite')
    op.drop_column('consultations', 'observations')
    op.drop_column('consultations', 'antecedents_consultation')
