"""Set case_registered to non-nullable

Revision ID: 1873500a2866
Revises: 9b600b04a11c
Create Date: 2025-03-04 14:56:34.784251

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '1873500a2866'
down_revision = '9b600b04a11c'
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
