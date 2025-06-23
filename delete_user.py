#!/usr/bin/env python3
"""
Script to safely delete a user from the system.
This script will:
1. Find the user by username or email
2. Show user details for confirmation
3. Delete all associated data (items, notifications, reports, etc.)
4. Remove the user account
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app import create_app
from app.core.extensions import db
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.models.report import Report
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_user(username_or_email):
    """Find user by username or email."""
    app = create_app()
    
    with app.app_context():
        # Try to find by username first
        user = User.query.filter_by(username=username_or_email).first()
        if user:
            return user
        
        # Try to find by email
        user = User.query.filter_by(email=username_or_email).first()
        if user:
            return user
        
        return None

def get_user_stats(user):
    """Get statistics about user's data."""
    app = create_app()
    
    with app.app_context():
        items_count = Item.query.filter_by(user_id=user.id).count()
        notifications_count = Notification.query.filter_by(user_id=user.id).count()
        reports_count = Report.query.filter_by(user_id=user.id).count()
        
        return {
            'items': items_count,
            'notifications': notifications_count,
            'reports': reports_count
        }

def delete_user_safely(user):
    """Safely delete user and all associated data."""
    app = create_app()
    
    with app.app_context():
        try:
            user_id = user.id
            username = user.username
            email = user.email
            
            logger.info(f"Starting deletion of user: {username} ({email})")
            
            # Delete all reports associated with the user
            reports_deleted = Report.query.filter_by(user_id=user_id).delete()
            logger.info(f"Deleted {reports_deleted} reports")
            
            # Delete all items associated with the user
            items_deleted = Item.query.filter_by(user_id=user_id).delete()
            logger.info(f"Deleted {items_deleted} items")
            
            # Delete all notifications associated with the user
            notifications_deleted = Notification.query.filter_by(user_id=user_id).delete()
            logger.info(f"Deleted {notifications_deleted} notifications")
            
            # Delete the user
            db.session.delete(user)
            db.session.commit()
            
            logger.info(f"Successfully deleted user {username} and all associated data")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            db.session.rollback()
            return False

def main():
    """Main function to delete user."""
    username_or_email = "Vedanshi"
    
    print(f"Searching for user: {username_or_email}")
    
    # Find the user
    user = find_user(username_or_email)
    
    if not user:
        print(f"❌ User '{username_or_email}' not found in the system.")
        print("Please check the username or email and try again.")
        return False
    
    # Display user information
    print(f"\n📋 User Found:")
    print(f"   ID: {user.id}")
    print(f"   Username: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Created: {user.created_at}")
    print(f"   Verified: {'Yes' if user.is_verified else 'No'}")
    print(f"   Active: {'Yes' if user.is_active else 'No'}")
    
    # Get user statistics
    stats = get_user_stats(user)
    print(f"\n📊 User Data:")
    print(f"   Items: {stats['items']}")
    print(f"   Notifications: {stats['notifications']}")
    print(f"   Reports: {stats['reports']}")
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This action cannot be undone!")
    print(f"This will permanently delete:")
    print(f"   - User account: {user.username}")
    print(f"   - All items: {stats['items']}")
    print(f"   - All notifications: {stats['notifications']}")
    print(f"   - All reports: {stats['reports']}")
    print(f"   - All user data and settings")
    
    response = input(f"\nAre you sure you want to delete user '{user.username}'? (yes/NO): ")
    
    if response.lower() != 'yes':
        print("❌ Deletion cancelled.")
        return False
    
    # Final confirmation
    final_response = input(f"Type '{user.username}' to confirm deletion: ")
    
    if final_response != user.username:
        print("❌ Confirmation failed. Deletion cancelled.")
        return False
    
    # Delete the user
    print(f"\n🗑️  Deleting user '{user.username}'...")
    
    if delete_user_safely(user):
        print(f"✅ Successfully deleted user '{username_or_email}' and all associated data!")
        return True
    else:
        print(f"❌ Failed to delete user '{username_or_email}'. Check the logs for details.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1) 