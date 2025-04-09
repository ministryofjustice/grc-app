"""empty message

Revision ID: 5405bd8bc1c7
Revises: 463480f8213b
Create Date: 2025-04-09 14:02:13.618121

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '5405bd8bc1c7'
down_revision = '463480f8213b'
branch_labels = None
depends_on = None


def upgrade():
    # Set all NULL values in case_registered to False
    op.execute('UPDATE application SET case_registered = FALSE WHERE case_registered IS NULL')


def downgrade():
    pass
