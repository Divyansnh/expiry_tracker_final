"""Remove category system from items

Revision ID: remove_category_system
Revises: d5a62f833b74
Create Date: 2025-06-21 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'remove_category_system'
down_revision = 'd5a62f833b74'
branch_labels = None
depends_on = None


def upgrade():
    """Remove category system."""
    # Remove foreign key constraint from items table
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.drop_constraint('items_category_id_fkey', type_='foreignkey')
        batch_op.drop_column('category_id')
    
    # Drop the categories table
    op.drop_table('categories')


def downgrade():
    """Recreate category system (if needed)."""
    # Recreate categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Recreate category_id column in items table
    with op.batch_alter_table('items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('category_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('items_category_id_fkey', 'categories', ['category_id'], ['id']) 