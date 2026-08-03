"""add admin session version

Revision ID: aa1f7636940
Revises: 5405bd8bc1c7
Create Date: 2026-06-30 11:17:43.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aa1f7636940'
down_revision = '5405bd8bc1c7'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('admin_user', sa.Column('session_version', sa.String(length=32), nullable=True))
    op.execute("UPDATE admin_user SET session_version = md5(random()::text || clock_timestamp()::text) WHERE session_version IS NULL")
    op.alter_column('admin_user', 'session_version', nullable=False)


def downgrade():
    op.drop_column('admin_user', 'session_version')
