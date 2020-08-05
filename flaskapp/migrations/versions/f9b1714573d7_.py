"""empty message

Revision ID: f9b1714573d7
Revises: 71e2c1f3d64e
Create Date: 2020-07-30 16:09:45.299755

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f9b1714573d7'
down_revision = '71e2c1f3d64e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('available_player', sa.Column('pos', sa.String(length=5), nullable=True))
    op.add_column('available_player', sa.Column('thru', sa.String(length=5), nullable=True))
    op.add_column('available_player', sa.Column('to_par', sa.String(length=100), nullable=True))
    op.add_column('available_player', sa.Column('to_par_int', sa.Integer(), nullable=True))
    op.add_column('available_player', sa.Column('today', sa.String(length=50), nullable=True))
    op.add_column('available_player', sa.Column('today_int', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('available_player', 'today_int')
    op.drop_column('available_player', 'today')
    op.drop_column('available_player', 'to_par_int')
    op.drop_column('available_player', 'to_par')
    op.drop_column('available_player', 'thru')
    op.drop_column('available_player', 'pos')
    # ### end Alembic commands ###
