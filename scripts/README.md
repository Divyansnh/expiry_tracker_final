# Scripts Directory

This directory contains various utility scripts for managing and maintaining the application.

## Directory Structure

### Database Scripts (`database/`)
- `setup_db.py` - Initialize and set up the database
- `db_utils.py` - Database utility functions
- `check_test_data.py` - Verify test data in the database
- `check_users.py` - List and check user accounts
- `create_backup.py` - Create database backups
- `backups/` - Directory containing database backups

### Notification Scripts (`notifications/`)
- `check_notifications.py` - Check notification status
- `check_notification_status.py` - Detailed notification status check
- `fix_notifications.py` - Fix notification issues
- `verify_notifications.py` - Verify notification system
- `test_zero_days_notification.py` - Test notifications for items expiring today
- `test_notification_changes.py` - Test notification system changes
- `send_real_notification.py` - Send actual test notifications

### Cleanup Scripts (`cleanup/`)
- `cleanup_test_data.py` - Remove test data
- `delete_user.py` - Delete user accounts
- `delete_vedanshi.py` - Specific user deletion script
- `verify_deletion.py` - Verify deletion operations

### Utility Scripts (`utilities/`)
- `create_test_image.py` - Create test images for development

### Test Scripts (`tests/`)
- Contains test-specific scripts and utilities

## Usage

Each script can be run directly using Python from the project root:

```bash
python -m scripts.database.setup_db
python -m scripts.notifications.check_notifications
# etc.
```

## Best Practices

1. Always run scripts from the project root directory
2. Check script documentation for required environment variables
3. Back up data before running destructive scripts
4. Test scripts in development environment first

## Adding New Scripts

When adding new scripts:
1. Place them in the appropriate category directory
2. Update this README
3. Include docstrings and comments
4. Add error handling
5. Log important operations

# Database Scripts

This directory contains scripts for managing the Expiry Tracker application's database.

## Database Utilities (`db_utils.py`)

The `db_utils.py` script provides comprehensive database management and verification tools.

### Features

1. **Database Connection Check**
   - Verifies PostgreSQL connection
   - Checks database version
   - Verifies table existence
   - Counts records in tables

2. **Schema Verification**
   - Lists all tables
   - Checks column definitions
   - Verifies indexes
   - Validates foreign key constraints

3. **Model Structure Check**
   - Verifies SQLAlchemy model definitions
   - Checks table relationships
   - Validates column mappings

### Usage

To run a complete database verification:
```bash
python scripts/db_utils.py
```

To use specific functions in your code:
```python
from scripts.db_utils import (
    check_database_connection,
    check_database_schema,
    check_model_structure,
    verify_database
)

# Check only database connection
check_database_connection()

# Check only schema
check_database_schema()

# Check only model structure
check_model_structure()

# Run complete verification
verify_database()
```

## Database Setup (`setup_db.py`)

The `setup_db.py` script handles initial database setup and configuration.

### Prerequisites

1. Python 3.6 or higher
2. PostgreSQL database server
3. Required Python packages (install using `pip install -r requirements.txt`)

### Usage

1. Make sure you have a PostgreSQL database server running
2. Run the setup script:
   ```bash
   python scripts/setup_db.py
   ```

The script will:
- Check for required environment variables
- Create a `.env` file with default values if it doesn't exist
- Initialize the database tables
- Run any pending migrations

### Environment Variables

The script requires the following environment variables to be set:

- `DATABASE_URL`: PostgreSQL connection URL (e.g., `postgresql://username:password@localhost:5432/dbname`)
- `SECRET_KEY`: Flask secret key for session management
- `MAIL_SERVER`: SMTP server for email notifications
- `MAIL_PORT`: SMTP server port
- `MAIL_USERNAME`: SMTP username
- `MAIL_PASSWORD`: SMTP password

### Example `.env` File

```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/expiry_tracker

# Security
SECRET_KEY=your-secret-key-here

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Optional Configuration
FLASK_ENV=development
DEBUG=True
```

## Troubleshooting

If you encounter any issues:

1. Make sure PostgreSQL is running and accessible
2. Verify your database credentials in the `.env` file
3. Check that all required Python packages are installed
4. Ensure you have write permissions in the project directory

For more detailed database documentation, see the [Database Documentation](../docs/database/README.md). 