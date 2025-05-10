"""Initial migration

Revision ID: initial_migration
Revises: 
Create Date: 2024-04-06 13:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = 'initial_migration'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # All columns already exist, no changes needed
    pass

def downgrade():
    # No changes to revert
    pass 