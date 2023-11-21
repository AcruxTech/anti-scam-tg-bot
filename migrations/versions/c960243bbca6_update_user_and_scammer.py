"""Update user and scammer

Revision ID: c960243bbca6
Revises: bd09eaf82e41
Create Date: 2023-11-21 18:51:57.206460

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c960243bbca6'
down_revision = 'bd09eaf82e41'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('scammers', 'last_name')
    op.drop_column('users', 'last_name')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('scammers', sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
