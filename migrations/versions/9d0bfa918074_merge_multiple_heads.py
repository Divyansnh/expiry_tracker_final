"""merge multiple heads

Revision ID: 9d0bfa918074
Revises: bdaddb1d9553, cleanup_in_app_notifications
Create Date: 2025-04-19 12:12:47.717462

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d0bfa918074'
down_revision = ('bdaddb1d9553', 'cleanup_in_app_notifications')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
