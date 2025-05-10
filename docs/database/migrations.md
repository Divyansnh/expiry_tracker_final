# Database Migrations Documentation

## Overview
This document describes the database migration history and process for the Expiry Tracker application. Migrations are managed using Alembic and follow a sequential versioning system.

## Migration Process

### Creating Migrations
1. Make changes to SQLAlchemy models
2. Generate migration script:
   ```bash
   flask db migrate -m "description of changes"
   ```
3. Review and edit the generated migration script
4. Apply the migration:
   ```bash
   flask db upgrade
   ```

### Rolling Back Migrations
To rollback to a previous version:
```bash
flask db downgrade [revision]
```

## Migration History

### 1. Initial Migration
- Created base tables: users, items, notifications, reports, categories
- Established basic relationships and constraints
- Set up initial indexes

### 2. Add Security Fields
- Added security question and answer fields to users table
- Added two-factor authentication fields
- Added login attempt tracking fields
- Added account locking mechanism

### 3. Fix Users Table
- Updated user model constraints
- Added missing fields for user management
- Fixed foreign key relationships

### 4. Add Status Column to Notifications
- Added status column to notifications table
- Updated notification model to track read/unread status
- Added read_at timestamp field

### 5. Cleanup In-App Notifications
- Removed redundant notification fields
- Simplified notification structure
- Updated notification status handling

### 6. Fix Report Date Constraint
- Added unique constraint on user_id and date
- Updated report model to handle daily reports
- Fixed report data structure

## Current Schema Version
The current schema version is: `fix_report_date`

## Migration Tools

### Alembic Commands
- `flask db init`: Initialize migration environment
- `flask db migrate`: Create new migration
- `flask db upgrade`: Apply migrations
- `flask db downgrade`: Rollback migrations
- `flask db current`: Show current revision
- `flask db history`: Show migration history

### Migration Script Structure
```python
"""description of changes

Revision ID: revision_id
Revises: previous_revision
Create Date: creation_date

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Migration code
    pass

def downgrade():
    # Rollback code
    pass
```

## Best Practices

### Creating Migrations
1. Always test migrations in development first
2. Include both upgrade and downgrade paths
3. Document changes in migration message
4. Keep migrations atomic and focused
5. Test rollback functionality

### Applying Migrations
1. Backup database before applying migrations
2. Apply migrations in order
3. Verify data integrity after migration
4. Test application functionality
5. Document any manual steps required

### Migration Naming
- Use descriptive names
- Include date prefix (YYYYMMDD)
- Use lowercase with underscores
- Example: `20240419_fix_report_date_constraint.py`

## Troubleshooting

### Common Issues
1. **Migration Conflicts**
   - Resolve by merging heads
   - Use `flask db merge heads`

2. **Failed Migrations**
   - Check error messages
   - Verify database state
   - Rollback if necessary

3. **Missing Revisions**
   - Verify migration files exist
   - Check alembic_version table
   - Recreate missing migrations if needed

### Recovery Procedures
1. **Database Backup**
   ```bash
   pg_dump -U username -d database_name > backup.sql
   ```

2. **Migration Reset**
   ```bash
   flask db stamp head
   flask db upgrade
   ```

3. **Manual Fixes**
   - Edit migration scripts if needed
   - Update database directly if necessary
   - Document all manual changes

## Related Documentation
- [Database Schema](schema.md)
- [Models Documentation](../developer/models.md)
- [Database Configuration](../developer/configuration.md) 