"""empty message

Revision ID: ea1061ba5f6e
Revises: 25c7409c8d3f
Create Date: 2024-08-21 14:26:49.265760

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea1061ba5f6e'
down_revision = '25c7409c8d3f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recomeded_speed', schema=None) as batch_op:
        batch_op.add_column(sa.Column('Microhardness', sa.Float(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('recomeded_speed', schema=None) as batch_op:
        batch_op.drop_column('Microhardness')

    # ### end Alembic commands ###
