"""empty message

Revision ID: 50de901573c9
Revises: 59213421de7c
Create Date: 2020-08-03 07:37:37.141555

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '50de901573c9'
down_revision = '59213421de7c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('available_player', sa.Column('cut_final', sa.Integer(), nullable=True))
    op.add_column('available_player', sa.Column('cut_projected', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('available_player', 'cut_projected')
    op.drop_column('available_player', 'cut_final')
    # ### end Alembic commands ###
