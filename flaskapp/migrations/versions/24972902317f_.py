"""empty message

Revision ID: 24972902317f
Revises: 1bde48b248a4
Create Date: 2020-08-02 17:51:10.453082

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '24972902317f'
down_revision = '1bde48b248a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('active_for_tournament', sa.Integer(), nullable=True))
    op.add_column('user', sa.Column('paypal', sa.String(length=120), nullable=True))
    op.add_column('user', sa.Column('venmo', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'venmo')
    op.drop_column('user', 'paypal')
    op.drop_column('user', 'active_for_tournament')
    # ### end Alembic commands ###
