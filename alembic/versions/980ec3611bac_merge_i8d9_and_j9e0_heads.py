"""merge_i8d9_and_j9e0_heads

Revision ID: 980ec3611bac
Revises: i8d9e0f1a2b3, j9e0f1a2b3c4
Create Date: 2026-06-18 18:34:44.345979

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '980ec3611bac'
down_revision: Union[str, None] = ('i8d9e0f1a2b3', 'j9e0f1a2b3c4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
