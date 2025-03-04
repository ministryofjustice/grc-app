"""Add case_registered to Application model

Revision ID: 0485fe207886
Revises: 6adf7ebb3032
Create Date: 2025-03-04 14:25:35.551840

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '0485fe207886'
down_revision = '6adf7ebb3032'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('application', schema=None) as batch_op:
        batch_op.alter_column('case_registered',
               existing_type=sa.BOOLEAN(),
               nullable=True)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('application', schema=None) as batch_op:
        batch_op.alter_column('case_registered',
               existing_type=sa.BOOLEAN(),
               nullable=False)

    # ### end Alembic commands ###
