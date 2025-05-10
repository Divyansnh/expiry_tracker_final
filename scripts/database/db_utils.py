#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path
from sqlalchemy import inspect, create_engine, MetaData, Table
import psycopg2
from psycopg2.extras import RealDictCursor

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app
from app.core.extensions import db
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.models.report import Report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_database_connection():
    """Check database connection and basic structure."""
    try:
        # Check direct PostgreSQL connection
        conn = psycopg2.connect(
            dbname="expiry_tracker",
            host="localhost"
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        logger.info("\n=== Direct Database Connection Check ===")
        cur.execute("SELECT version();")
        result = cur.fetchone()
        if result:
            logger.info(f"PostgreSQL Version: {result['version']}")
        else:
            logger.warning("Could not fetch PostgreSQL version")
        
        # Check if users table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            );
        """)
        result = cur.fetchone()
        table_exists = result['exists'] if result else False
        logger.info(f"Users table exists: {table_exists}")
        
        if table_exists:
            cur.execute("SELECT COUNT(*) as count FROM users;")
            result = cur.fetchone()
            user_count = result['count'] if result else 0
            logger.info(f"Number of users: {user_count}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error checking database connection: {str(e)}")
        return False
    return True

def check_database_schema():
    """Check database schema and structure."""
    app = create_app()
    with app.app_context():
        inspector = inspect(db.engine)
        
        logger.info("\n=== Database Schema Check ===")
        for table_name in inspector.get_table_names():
            logger.info(f"\nTable: {table_name}")
            
            # Check columns
            columns = inspector.get_columns(table_name)
            logger.info("Columns:")
            for column in columns:
                logger.info(f"  {column['name']}: {column['type']}")
            
            # Check indexes
            indexes = inspector.get_indexes(table_name)
            if indexes:
                logger.info("Indexes:")
                for index in indexes:
                    logger.info(f"  {index['name']}: {index['column_names']}")
            
            # Check foreign keys
            foreign_keys = inspector.get_foreign_keys(table_name)
            if foreign_keys:
                logger.info("Foreign Keys:")
                for fk in foreign_keys:
                    logger.info(f"  {fk['name']}: {fk['referred_table']}.{fk['referred_columns']}")

def check_model_structure():
    """Check SQLAlchemy model structure and relationships."""
    app = create_app()
    with app.app_context():
        logger.info("\n=== Model Structure Check ===")
        inspector = inspect(db.engine)
        
        # Check Users table
        logger.info("\nUsers table:")
        if 'users' in inspector.get_table_names():
            columns = inspector.get_columns('users')
            user_columns = [col['name'] for col in columns]
            logger.info(f"Columns: {user_columns}")
        
        # Check Items table
        logger.info("\nItems table:")
        if 'items' in inspector.get_table_names():
            columns = inspector.get_columns('items')
            item_columns = [col['name'] for col in columns]
            logger.info(f"Columns: {item_columns}")
        
        # Check Notifications table
        logger.info("\nNotifications table:")
        if 'notifications' in inspector.get_table_names():
            columns = inspector.get_columns('notifications')
            notification_columns = [col['name'] for col in columns]
            logger.info(f"Columns: {notification_columns}")
        
        # Check Reports table
        logger.info("\nReports table:")
        if 'reports' in inspector.get_table_names():
            columns = inspector.get_columns('reports')
            report_columns = [col['name'] for col in columns]
            logger.info(f"Columns: {report_columns}")
        
        # Check relationships
        logger.info("\nChecking relationships:")
        logger.info(f"User -> Items: {hasattr(User, 'items')}")
        logger.info(f"User -> Notifications: {hasattr(User, 'notifications')}")
        logger.info(f"User -> Reports: {hasattr(User, 'reports')}")
        logger.info(f"Item -> Notifications: {hasattr(Item, 'notifications')}")
        logger.info(f"Item -> User: {hasattr(Item, 'user')}")
        logger.info(f"Notification -> User: {hasattr(Notification, 'user')}")
        logger.info(f"Notification -> Item: {hasattr(Notification, 'item')}")
        logger.info(f"Report -> User: {hasattr(Report, 'user')}")

def verify_database():
    """Run comprehensive database verification."""
    logger.info("Starting database verification...")
    
    # Check connection
    if not check_database_connection():
        logger.error("Database connection check failed!")
        return False
    
    # Check schema
    check_database_schema()
    
    # Check model structure
    check_model_structure()
    
    logger.info("Database verification completed successfully!")
    return True

if __name__ == '__main__':
    verify_database() 