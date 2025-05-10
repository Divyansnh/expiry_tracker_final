"""fix report date constraint

Revision ID: fix_report_date
Revises: 9d0bfa918074
Create Date: 2024-04-19 11:39:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fix_report_date'
down_revision = '9d0bfa918074'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the existing unique constraint on date
    op.drop_constraint('reports_date_key', 'reports', type_='unique')
    
    # Create a new unique constraint on both date and user_id
    op.create_unique_constraint('reports_date_user_key', 'reports', ['date', 'user_id'])


def downgrade():
    # Drop the new unique constraint
    op.drop_constraint('reports_date_user_key', 'reports', type_='unique')
    
    # Recreate the original unique constraint on date
    op.create_unique_constraint('reports_date_key', 'reports', ['date']) 