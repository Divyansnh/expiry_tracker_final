#!/usr/bin/env python3
"""
Test script to verify notification system changes.
This script tests:
1. Default notification status (should be 'pending')
2. Notification creation through NotificationService
3. Status change functionality
"""

import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.models.notification import Notification
from app.models.user import User
from app.models.item import Item
from app.services.notification_service import NotificationService
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
        
        # Create a test item
        test_item = Item(
            name='Test Item',
            expiry_date=datetime.utcnow() + timedelta(days=1),
            user_id=test_user.id
        )
        db.session.add(test_item)
        db.session.commit()
        
        # Test 1: Create notification through NotificationService
        notification_service = NotificationService()
        notification = notification_service.create_notification(
            user_id=test_user.id,
            item_id=test_item.id,
            message='Test notification through service',
            type='email',
            priority='normal'
        )
        
        if notification:
            print("\nTest 1: Created notification through service")
            print(f"- Message: {notification.message}")
            print(f"- Status: {notification.status} (should be 'pending')")
            print(f"- Type: {notification.type}")
            print(f"- Priority: {notification.priority}")
        else:
            print("\nTest 1: Failed to create notification")
            return
            
        # Test 2: Verify default status is 'pending'
        if notification.status == 'pending':
            print("\nTest 2: ✅ Default status is 'pending'")
        else:
            print("\nTest 2: ❌ Default status is not 'pending'")
            
        # Test 3: Mark notification as sent
        notification.mark_as_read()
        db.session.commit()
        
        # Verify status change
        updated_notification = Notification.query.get(notification.id)
        if updated_notification.status == 'sent':
            print("\nTest 3: ✅ Successfully marked notification as sent")
        else:
            print("\nTest 3: ❌ Failed to mark notification as sent")
            
        # Clean up
        Notification.query.filter_by(user_id=test_user.id).delete()
        Item.query.filter_by(user_id=test_user.id).delete()
        db.session.commit()
        print("\nCleaned up test data")

if __name__ == '__main__':
    test_notification_changes() 