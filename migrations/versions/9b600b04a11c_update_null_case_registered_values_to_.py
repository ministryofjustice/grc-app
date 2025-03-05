"""Update null case_registered values to False

Revision ID: 9b600b04a11c
Revises: 0485fe207886
Create Date: 2025-03-04 14:34:55.527953

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils


# revision identifiers, used by Alembic.
revision = '9b600b04a11c'
down_revision = '0485fe207886'
branch_labels = None
depends_on = None


def upgrade():
    # Set all NULL values in case_registered to False
    op.execute('UPDATE application SET case_registered = FALSE WHERE case_registered IS NULL')


def downgrade():
    pass
