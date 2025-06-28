#!/usr/bin/env python3
"""
Script to delete a user from the system.

This script will:
1. Find the user by username or email
2. Delete all associated data (items, activities, notifications, reports)
3. Delete the user account
4. Log the deletion process

Usage:
    python scripts/utils/delete_user.py --username "Vedanshi"
    python scripts/utils/delete_user.py --email "vedanshi@example.com"
"""

import sys
import os
import argparse
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from app import create_app
from app.core.extensions import db
from app.models.user import User
from app.models.item import Item
from app.models.activity import Activity
from app.models.notification import Notification
from app.models.report import Report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def delete_user_data(user_id: int) -> dict:
    """
    Delete all data associated with a user.
    
    Args:
        user_id: The ID of the user to delete
        
    Returns:
        dict: Summary of deleted data
    """
    summary = {
        'items_deleted': 0,
        'activities_deleted': 0,
        'notifications_deleted': 0,
        'reports_deleted': 0,
        'user_deleted': False,
        'errors': []
    }
    
    try:
        # Delete items
        items = Item.query.filter_by(user_id=user_id).all()
        for item in items:
            try:
                db.session.delete(item)
                summary['items_deleted'] += 1
                logger.info(f"Deleted item: {item.name} (ID: {item.id})")
            except Exception as e:
                error_msg = f"Error deleting item {item.id}: {str(e)}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        # Delete activities
        activities = Activity.query.filter_by(user_id=user_id).all()
        for activity in activities:
            try:
                db.session.delete(activity)
                summary['activities_deleted'] += 1
                logger.info(f"Deleted activity: {activity.activity_type} (ID: {activity.id})")
            except Exception as e:
                error_msg = f"Error deleting activity {activity.id}: {str(e)}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        # Delete notifications
        notifications = Notification.query.filter_by(user_id=user_id).all()
        for notification in notifications:
            try:
                db.session.delete(notification)
                summary['notifications_deleted'] += 1
                logger.info(f"Deleted notification (ID: {notification.id})")
            except Exception as e:
                error_msg = f"Error deleting notification {notification.id}: {str(e)}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        # Delete reports
        reports = Report.query.filter_by(user_id=user_id).all()
        for report in reports:
            try:
                db.session.delete(report)
                summary['reports_deleted'] += 1
                logger.info(f"Deleted report for date: {report.date} (ID: {report.id})")
            except Exception as e:
                error_msg = f"Error deleting report {report.id}: {str(e)}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        # Delete the user
        user = User.query.get(user_id)
        if user:
            try:
                db.session.delete(user)
                summary['user_deleted'] = True
                logger.info(f"Deleted user: {user.username} (ID: {user.id})")
            except Exception as e:
                error_msg = f"Error deleting user {user_id}: {str(e)}"
                logger.error(error_msg)
                summary['errors'].append(error_msg)
        
        # Commit all changes
        db.session.commit()
        logger.info("Successfully committed all deletions to database")
        
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error during deletion process: {str(e)}"
        logger.error(error_msg)
        summary['errors'].append(error_msg)
        raise
    
    return summary

def find_user(username: str | None = None, email: str | None = None) -> User:
    """
    Find a user by username or email.
    
    Args:
        username: Username to search for
        email: Email to search for
        
    Returns:
        User: The found user object
        
    Raises:
        ValueError: If user is not found
    """
    user = None
    
    if username:
        user = User.query.filter_by(username=username).first()
        if user:
            logger.info(f"Found user by username: {username}")
            return user
    
    if email:
        user = User.query.filter_by(email=email).first()
        if user:
            logger.info(f"Found user by email: {email}")
            return user
    
    raise ValueError(f"User not found with username='{username}' or email='{email}'")

def confirm_deletion(user: User) -> bool:
    """
    Ask for confirmation before deleting the user.
    
    Args:
        user: The user to be deleted
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    print("\n" + "="*60)
    print("USER DELETION CONFIRMATION")
    print("="*60)
    print(f"Username: {user.username}")
    print(f"Email: {user.email}")
    print(f"User ID: {user.id}")
    print(f"Created: {user.created_at}")
    print(f"Is Admin: {user.is_admin}")
    print(f"Is Active: {user.is_active}")
    print(f"Is Verified: {user.is_verified}")
    
    # Count associated data
    items_count = Item.query.filter_by(user_id=user.id).count()
    activities_count = Activity.query.filter_by(user_id=user.id).count()
    notifications_count = Notification.query.filter_by(user_id=user.id).count()
    reports_count = Report.query.filter_by(user_id=user.id).count()
    
    print(f"\nAssociated Data:")
    print(f"  Items: {items_count}")
    print(f"  Activities: {activities_count}")
    print(f"  Notifications: {notifications_count}")
    print(f"  Reports: {reports_count}")
    
    print("\n" + "="*60)
    print("WARNING: This action will permanently delete the user and ALL associated data!")
    print("This action cannot be undone.")
    print("="*60)
    
    while True:
        response = input("\nAre you sure you want to delete this user? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'.")

def main():
    """Main function to handle user deletion."""
    parser = argparse.ArgumentParser(description='Delete a user from the system')
    parser.add_argument('--username', help='Username of the user to delete')
    parser.add_argument('--email', help='Email of the user to delete')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    
    args = parser.parse_args()
    
    if not args.username and not args.email:
        parser.error("Either --username or --email must be provided")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Find the user
            user = find_user(username=args.username, email=args.email)
            
            if args.dry_run:
                print("\n" + "="*60)
                print("DRY RUN - NO DATA WILL BE DELETED")
                print("="*60)
                print(f"User found: {user.username} ({user.email})")
                print(f"User ID: {user.id}")
                
                # Count associated data
                items_count = Item.query.filter_by(user_id=user.id).count()
                activities_count = Activity.query.filter_by(user_id=user.id).count()
                notifications_count = Notification.query.filter_by(user_id=user.id).count()
                reports_count = Report.query.filter_by(user_id=user.id).count()
                
                print(f"\nData that would be deleted:")
                print(f"  Items: {items_count}")
                print(f"  Activities: {activities_count}")
                print(f"  Notifications: {notifications_count}")
                print(f"  Reports: {reports_count}")
                print(f"  User account: 1")
                print("\nTotal records that would be deleted:", items_count + activities_count + notifications_count + reports_count + 1)
                return
            
            # Confirm deletion unless --force is used
            if not args.force:
                if not confirm_deletion(user):
                    print("Deletion cancelled.")
                    return
            
            # Delete the user and all associated data
            logger.info(f"Starting deletion process for user: {user.username} (ID: {user.id})")
            
            summary = delete_user_data(user.id)
            
            # Print summary
            print("\n" + "="*60)
            print("DELETION SUMMARY")
            print("="*60)
            print(f"Items deleted: {summary['items_deleted']}")
            print(f"Activities deleted: {summary['activities_deleted']}")
            print(f"Notifications deleted: {summary['notifications_deleted']}")
            print(f"Reports deleted: {summary['reports_deleted']}")
            print(f"User deleted: {'Yes' if summary['user_deleted'] else 'No'}")
            
            if summary['errors']:
                print(f"\nErrors encountered: {len(summary['errors'])}")
                for error in summary['errors']:
                    print(f"  - {error}")
            
            total_deleted = (summary['items_deleted'] + summary['activities_deleted'] + 
                           summary['notifications_deleted'] + summary['reports_deleted'] + 
                           (1 if summary['user_deleted'] else 0))
            
            print(f"\nTotal records deleted: {total_deleted}")
            
            if summary['user_deleted']:
                print("\n✅ User deletion completed successfully!")
            else:
                print("\n❌ User deletion failed!")
                
        except ValueError as e:
            logger.error(f"User not found: {str(e)}")
            print(f"Error: {str(e)}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            print(f"Error: {str(e)}")
            sys.exit(1)

if __name__ == '__main__':
    main() 