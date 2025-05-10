#!/usr/bin/env python3
import logging
import os
import sys
from datetime import datetime

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from app import create_app
    from app.core.extensions import db
    from sqlalchemy import text
except ImportError as e:
    logger.error(f"Failed to import required modules: {str(e)}")
    logger.error("Please make sure you're in the correct directory and virtual environment is activated")
    sys.exit(1)

def backup_notifications():
    """Create a backup of the notifications table."""
    backup_dir = 'backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'{backup_dir}/notifications_backup_{timestamp}.sql'
    
    with open(backup_file, 'w') as f:
        # Get all notifications
        result = db.session.execute(text("""
            SELECT * FROM notifications
        """))
        
        # Write CREATE TABLE statement
        f.write("CREATE TABLE IF NOT EXISTS notifications_backup AS SELECT * FROM notifications;\n")
        
        logger.info(f"Created backup at {backup_file}")
        return backup_file

def fix_notifications():
    """Fix the notifications table structure."""
    try:
        app = create_app()
    except Exception as e:
        logger.error(f"Failed to create Flask app: {str(e)}")
        sys.exit(1)
    
    with app.app_context():
        try:
            logger.info("Starting notification table fix...")
            
            # 1. Create backup
            backup_file = backup_notifications()
            logger.info(f"Backup created at {backup_file}")
            
            # 2. Check current state
            logger.info("Checking current notification table state...")
            result = db.session.execute(text("""
                SELECT COUNT(*) as null_status_count 
                FROM notifications 
                WHERE status IS NULL
            """))
            null_count = result.scalar() or 0
            logger.info(f"Found {null_count} notifications with null status")
            
            # 3. Update null status values to 'pending'
            if null_count > 0:
                logger.info("Updating null status values to 'pending'...")
                db.session.execute(text("""
                    UPDATE notifications 
                    SET status = 'pending' 
                    WHERE status IS NULL
                """))
            
            # 4. Drop is_read column if it exists
            logger.info("Checking for is_read column...")
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'notifications' 
                AND column_name = 'is_read'
            """))
            if result.scalar():
                logger.info("Dropping is_read column...")
                db.session.execute(text("""
                    ALTER TABLE notifications 
                    DROP COLUMN is_read
                """))
            
            # 5. Make status column non-nullable with default
            logger.info("Making status column non-nullable...")
            db.session.execute(text("""
                ALTER TABLE notifications 
                ALTER COLUMN status SET NOT NULL,
                ALTER COLUMN status SET DEFAULT 'pending'
            """))
            
            # 6. Add check constraint for status
            logger.info("Adding status check constraint...")
            try:
                db.session.execute(text("""
                    ALTER TABLE notifications 
                    ADD CONSTRAINT check_notification_status 
                    CHECK (status IN ('pending', 'sent'))
                """))
            except Exception as e:
                logger.warning(f"Could not add status constraint: {str(e)}")
            
            # Commit all changes
            db.session.commit()
            logger.info("Successfully fixed notification table structure!")
            
            # Verify the changes
            logger.info("Verifying changes...")
            result = db.session.execute(text("""
                SELECT COUNT(*) as total,
                       COUNT(CASE WHEN status = 'pending' THEN 1 END) as pending,
                       COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent
                FROM notifications
            """))
            row = result.fetchone()
            if row:
                logger.info(f"Verification complete. Total: {row[0]}, Pending: {row[1]}, Sent: {row[2]}")
            else:
                logger.info("No notifications found in the table")
            
        except Exception as e:
            logger.error(f"Error fixing notification table: {str(e)}")
            db.session.rollback()
            logger.info("Changes rolled back due to error")
            sys.exit(1)

if __name__ == '__main__':
    fix_notifications() 