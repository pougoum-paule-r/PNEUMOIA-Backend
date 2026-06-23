"""add_requetes_medecins_table

Revision ID: a0b1c2d3e4f5
Revises: 980ec3611bac
Create Date: 2026-06-22 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a0b1c2d3e4f5'
down_revision: Union[str, None] = '980ec3611bac'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'requetes_medecins',
        sa.Column('id',            sa.String(length=20),  nullable=False),
        sa.Column('medecin_id',    sa.String(length=15),  nullable=False),
        sa.Column('nom_medecin',   sa.String(length=300), nullable=True),
        sa.Column('email_medecin', sa.String(length=300), nullable=True),
        sa.Column('titre',         sa.String(length=300), nullable=False),
        sa.Column('categorie',
                  sa.Enum('bug_technique', 'probleme_acces', 'erreur_ia',
                          'lenteur', 'interface', 'autre', name='categorie_requete'),
                  nullable=False, server_default='autre'),
        sa.Column('description',   sa.Text(),  nullable=False),
        sa.Column('statut',
                  sa.Enum('en_attente', 'en_cours', 'resolu', 'ferme', name='statut_requete'),
                  nullable=False, server_default='en_attente'),
        sa.Column('action_admin',  sa.String(length=300), nullable=True),
        sa.Column('reponse_admin', sa.Text(),             nullable=True),
        sa.Column('repondu_par',   sa.String(length=15),  nullable=True),
        sa.Column('repondu_le',    sa.DateTime(),         nullable=True),
        sa.Column('created_at',    sa.DateTime(),         nullable=False),
        sa.Column('traite_le',     sa.DateTime(),         nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_requetes_medecins_medecin_id', 'requetes_medecins', ['medecin_id'])
    op.create_index('ix_requetes_medecins_statut',     'requetes_medecins', ['statut'])


def downgrade() -> None:
    op.drop_index('ix_requetes_medecins_statut',     table_name='requetes_medecins')
    op.drop_index('ix_requetes_medecins_medecin_id', table_name='requetes_medecins')
    op.drop_table('requetes_medecins')
    op.execute("DROP TYPE IF EXISTS categorie_requete")
    op.execute("DROP TYPE IF EXISTS statut_requete")
