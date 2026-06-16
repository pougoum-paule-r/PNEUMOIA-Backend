"""add all missing columns (idempotent — IF NOT EXISTS sur toutes les tables)

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-06-15 00:00:00.000000

Couvre toutes les colonnes ajoutées aux modèles mais jamais migrées
car create_all ne modifie pas les tables existantes.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, None] = 'e4f5a6b7c8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _exec(sql: str) -> None:
    op.get_bind().execute(sa.text(sql))


def upgrade() -> None:
    # ── TABLE medecins ────────────────────────────────────────────────────────
    # telephone/adresse/bio/website — normalement dans a1b2c3d4e5f6 mais parfois déjà là
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS telephone VARCHAR(30)")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS adresse VARCHAR(300)")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS bio TEXT")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS website VARCHAR(300)")

    # linkedin — manquant car bug typo dans a1b2c3d4e5f6 ('medecins ' avec espace)
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS linkedin VARCHAR(300)")

    # Validation / rejet du dossier
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS motif_rejet TEXT")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS valide_par VARCHAR(15) REFERENCES admins(id) ON DELETE SET NULL")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS valide_le TIMESTAMP")

    # Activation du compte (lien email après validation admin)
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS activation_token VARCHAR(255)")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS activation_expires TIMESTAMP")

    # Code référent (parrainage aides-soignants)
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS code_referent VARCHAR(10)")
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS code_referent_actif BOOLEAN NOT NULL DEFAULT TRUE")
    _exec("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_constraint
                WHERE conname = 'medecins_code_referent_key'
                  AND conrelid = 'medecins'::regclass
            ) THEN
                ALTER TABLE medecins ADD CONSTRAINT medecins_code_referent_key UNIQUE (code_referent);
            END IF;
        END $$
    """)

    # Préférences utilisateur
    _exec("ALTER TABLE medecins ADD COLUMN IF NOT EXISTS preferences JSONB DEFAULT '{}'")

    # ── TABLE patients ────────────────────────────────────────────────────────
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS civilite VARCHAR(10)")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS adresse VARCHAR(300)")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS profession VARCHAR(150)")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS personne_a_contacter VARCHAR(150)")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS telephone_urgence VARCHAR(20)")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS deleted_by VARCHAR(15) REFERENCES medecins(id) ON DELETE SET NULL")
    _exec("ALTER TABLE patients ADD COLUMN IF NOT EXISTS aide_id VARCHAR(15) REFERENCES aides_soignants(id) ON DELETE SET NULL")

    # ── TABLE consultations ───────────────────────────────────────────────────
    _exec("ALTER TABLE consultations ADD COLUMN IF NOT EXISTS antecedents_consultation JSONB")
    _exec("ALTER TABLE consultations ADD COLUMN IF NOT EXISTS observations TEXT")
    _exec("""
        DO $$ BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'statut_clinique_enum'
            ) THEN
                CREATE TYPE statut_clinique_enum AS ENUM ('stable','surveille','urgent','critique');
            END IF;
        END $$
    """)
    _exec("ALTER TABLE consultations ADD COLUMN IF NOT EXISTS statut_clinique statut_clinique_enum")

    # ── TABLE otp_codes ───────────────────────────────────────────────────────
    _exec("ALTER TABLE otp_codes ADD COLUMN IF NOT EXISTS purpose VARCHAR(20) NOT NULL DEFAULT 'login'")
    _exec("ALTER TABLE otp_codes ADD COLUMN IF NOT EXISTS fail_count INTEGER NOT NULL DEFAULT 0")


def downgrade() -> None:
    # otp_codes
    op.drop_column('otp_codes', 'fail_count')
    op.drop_column('otp_codes', 'purpose')
    # consultations
    op.drop_column('consultations', 'statut_clinique')
    op.drop_column('consultations', 'observations')
    op.drop_column('consultations', 'antecedents_consultation')
    # patients
    op.drop_column('patients', 'aide_id')
    op.drop_column('patients', 'deleted_by')
    op.drop_column('patients', 'deleted_at')
    op.drop_column('patients', 'updated_at')
    op.drop_column('patients', 'telephone_urgence')
    op.drop_column('patients', 'personne_a_contacter')
    op.drop_column('patients', 'profession')
    op.drop_column('patients', 'adresse')
    op.drop_column('patients', 'civilite')
    # medecins
    op.drop_column('medecins', 'preferences')
    op.drop_column('medecins', 'code_referent_actif')
    op.drop_column('medecins', 'code_referent')
    op.drop_column('medecins', 'activation_expires')
    op.drop_column('medecins', 'activation_token')
    op.drop_column('medecins', 'valide_le')
    op.drop_column('medecins', 'valide_par')
    op.drop_column('medecins', 'motif_rejet')
    op.drop_column('medecins', 'linkedin')
    op.drop_column('medecins', 'website')
    op.drop_column('medecins', 'bio')
    op.drop_column('medecins', 'adresse')
    op.drop_column('medecins', 'telephone')
