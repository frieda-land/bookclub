"""add number_of_books_read to trophy table

Revision ID: 204238475e74
Revises: d9118dafb6ad
Create Date: 2025-02-07 22:00:41.691851

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '204238475e74'
down_revision: Union[str, None] = 'd9118dafb6ad'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('trophy', sa.Column('number_of_books_read', sa.Integer(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('trophy', 'number_of_books_read')
    # ### end Alembic commands ###
