"""cleanup in app notifications

Revision ID: cleanup_in_app_notifications
Revises: 
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'cleanup_in_app_notifications'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Delete all in-app notifications
    op.execute("DELETE FROM notifications WHERE type = 'in_app'")

def downgrade():
    # No downgrade needed as this is a cleanup migration
    pass 