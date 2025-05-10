"""Add security fields to users table

Revision ID: add_security_fields
Revises: fix_users_table
Create Date: 2024-04-06 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_security_fields'
down_revision = 'fix_users_table'
branch_labels = None
depends_on = None

def upgrade():
    # Create the columns if they don't exist
    with op.batch_alter_table('users') as batch_op:
        # First check if columns exist
        conn = op.get_bind()
        inspector = sa.inspect(conn)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'login_attempts' not in columns:
            batch_op.add_column(sa.Column('login_attempts', sa.Integer(), nullable=True, server_default='0'))
        
        if 'locked_until' not in columns:
            batch_op.add_column(sa.Column('locked_until', sa.DateTime(), nullable=True))

def downgrade():
    # Remove the columns
    with op.batch_alter_table('users') as batch_op:
        batch_op.drop_column('login_attempts')
        batch_op.drop_column('locked_until') 