"""make trophy year attribute nullable False

Revision ID: 2bb3e78a6cce
Revises: c7afaf41f05d
Create Date: 2025-02-09 13:59:23.272991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2bb3e78a6cce'
down_revision: Union[str, None] = 'c7afaf41f05d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trophy', 'year',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('trophy', 'year',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###
