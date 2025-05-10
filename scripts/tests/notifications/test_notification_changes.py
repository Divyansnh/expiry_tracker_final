#!/usr/bin/env python3
"""
Test script to verify notification system changes.
This script tests:
1. Notification visibility
2. Pending notification filtering
3. Mark all as read functionality
4. Status updates
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.models.notification import Notification
from app.models.user import User
from app.core.extensions import db
from datetime import datetime, timedelta

def test_notification_changes():
    """Test notification system changes."""
    app = create_app()
    with app.app_context():
        # Get a test user
        test_user = User.query.first()
        if not test_user:
            print("No test user found")
            return
            
        print("\n=== Testing Notification Changes ===")
        
        # Create test notifications with different statuses
        notifications = [
            {
                'message': 'Test pending notification',
                'status': 'pending',
                'type': 'email',
                'priority': 'normal'
            },
            {
                'message': 'Test sent notification',
                'status': 'sent',
                'type': 'email',
                'priority': 'normal'
            }
        ]
        
        # Create notifications
        for notif_data in notifications:
            notification = Notification()
            notification.user_id = test_user.id
            notification.message = notif_data['message']
            notification.status = notif_data['status']
            notification.type = notif_data['type']
            notification.priority = notif_data['priority']
            notification.created_at = datetime.utcnow()
            
            try:
                db.session.add(notification)
                db.session.commit()
                print(f"Created {notif_data['status']} notification: {notif_data['message']}")
            except Exception as e:
                print(f"Error creating notification: {e}")
                db.session.rollback()
        
        # Test 1: Verify all notifications are visible
        all_notifications = Notification.query.filter_by(user_id=test_user.id).all()
        print(f"\nTest 1: All notifications visible ({len(all_notifications)} found)")
        for n in all_notifications:
            print(f"- {n.message} (Status: {n.status})")
            
        # Test 2: Verify only pending notifications can be marked as read
        pending_notifications = Notification.query.filter_by(
            user_id=test_user.id,
            status='pending'
        ).all()
        print(f"\nTest 2: Pending notifications ({len(pending_notifications)} found)")
        for n in pending_notifications:
            print(f"- {n.message}")
            
        # Test 3: Mark all pending as read
        for notification in pending_notifications:
            notification.status = 'sent'
        db.session.commit()
        print("\nTest 3: Marked all pending notifications as read")
        
        # Test 4: Verify status changes
        updated_notifications = Notification.query.filter_by(user_id=test_user.id).all()
        print("\nTest 4: Final notification statuses")
        for n in updated_notifications:
            print(f"- {n.message} (Status: {n.status})")
            
        # Clean up
        Notification.query.filter_by(user_id=test_user.id).delete()
        db.session.commit()
        print("\nCleaned up test notifications")

if __name__ == '__main__':
    test_notification_changes() 