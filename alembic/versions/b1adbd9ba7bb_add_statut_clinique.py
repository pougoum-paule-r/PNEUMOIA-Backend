"""add statut_clinique

Revision ID: b1adbd9ba7bb
Revises: b2c3d4e5f6a7
Create Date: 2026-06-07 00:40:42.773996

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = 'b1adbd9ba7bb'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'statut_clinique_enum') THEN
                CREATE TYPE statut_clinique_enum AS ENUM ('stable','surveille','urgent','critique');
            END IF;
        END $$
    """))
    conn.execute(sa.text(
        "ALTER TABLE consultations ADD COLUMN IF NOT EXISTS "
        "statut_clinique statut_clinique_enum"
    ))


def downgrade() -> None:
    op.drop_column('consultations', 'statut_clinique')
    op.execute("DROP TYPE IF EXISTS statut_clinique_enum")
