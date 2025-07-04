"""Add credential access verification fields

Revision ID: f86c0425fbe6
Revises: remove_category_system
Create Date: 2025-06-23 11:00:55.622999

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f86c0425fbe6'
down_revision = 'remove_category_system'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('apscheduler_jobs', schema=None) as batch_op:
        batch_op.drop_index('ix_apscheduler_jobs_next_run_time')

    op.drop_table('apscheduler_jobs')
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('credential_access_code', sa.String(length=6), nullable=True))
        batch_op.add_column(sa.Column('credential_access_code_expires_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('credential_access_verified', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('credential_access_expires_at', sa.DateTime(), nullable=True))
        batch_op.drop_index('idx_users_zoho_credential_fingerprint')
        batch_op.drop_column('zoho_last_credential_update')
        batch_op.drop_column('zoho_credential_version')
        batch_op.drop_column('zoho_credential_fingerprint')
        batch_op.drop_column('zoho_credential_usage_count')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('zoho_credential_usage_count', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('zoho_credential_fingerprint', sa.VARCHAR(length=64), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('zoho_credential_version', sa.INTEGER(), server_default=sa.text('1'), autoincrement=False, nullable=False))
        batch_op.add_column(sa.Column('zoho_last_credential_update', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
        batch_op.create_index('idx_users_zoho_credential_fingerprint', ['zoho_credential_fingerprint'], unique=False)
        batch_op.drop_column('credential_access_expires_at')
        batch_op.drop_column('credential_access_verified')
        batch_op.drop_column('credential_access_code_expires_at')
        batch_op.drop_column('credential_access_code')

    op.create_table('apscheduler_jobs',
    sa.Column('id', sa.VARCHAR(length=191), autoincrement=False, nullable=False),
    sa.Column('next_run_time', sa.DOUBLE_PRECISION(precision=53), autoincrement=False, nullable=True),
    sa.Column('job_state', postgresql.BYTEA(), autoincrement=False, nullable=False),
    sa.PrimaryKeyConstraint('id', name='apscheduler_jobs_pkey')
    )
    with op.batch_alter_table('apscheduler_jobs', schema=None) as batch_op:
        batch_op.create_index('ix_apscheduler_jobs_next_run_time', ['next_run_time'], unique=False)

    # ### end Alembic commands ###
