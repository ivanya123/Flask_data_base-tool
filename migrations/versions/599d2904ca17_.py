"""empty message

Revision ID: 599d2904ca17
Revises: ea1061ba5f6e
Create Date: 2024-09-20 09:08:13.648211

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '599d2904ca17'
down_revision = 'ea1061ba5f6e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('coefficients',
    sa.Column('material_id', sa.Integer(), nullable=False),
    sa.Column('coating_id', sa.Integer(), nullable=False),
    sa.Column('tool_id', sa.Integer(), nullable=False),
    sa.Column('cutting_force_coefficient', sa.Float(), nullable=False),
    sa.Column('cutting_temperature_coefficient', sa.Float(), nullable=False),
    sa.Column('durability_coefficient', sa.Float(), nullable=False),
    sa.ForeignKeyConstraint(['coating_id'], ['coating.id'], ),
    sa.ForeignKeyConstraint(['material_id'], ['material.id'], ),
    sa.ForeignKeyConstraint(['tool_id'], ['toolsdate.id'], ),
    sa.PrimaryKeyConstraint('material_id', 'coating_id', 'tool_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('coefficients')
    # ### end Alembic commands ###
