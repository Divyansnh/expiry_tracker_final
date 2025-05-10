"""Fix users table structure

Revision ID: fix_users_table
Revises: initial_migration
Create Date: 2024-04-06 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'fix_users_table'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None

def upgrade():
    # Add login_attempts column
    op.add_column('users', sa.Column('login_attempts', sa.Integer(), nullable=True, server_default='0'))
    
    # Add locked_until column
    op.add_column('users', sa.Column('locked_until', sa.DateTime(), nullable=True))

def downgrade():
    # Remove the columns
    op.drop_column('users', 'login_attempts')
    op.drop_column('users', 'locked_until') 