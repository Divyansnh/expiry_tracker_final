import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.tasks.cleanup import cleanup_expired_items
from app.core.extensions import db

def verify_notifications():
    """Verify notification system without affecting main database."""
    print("\nStarting notification system verification...")
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        try:
            # Clean up any existing test data first
            print("\nCleaning up any existing test data...")
            test_user = User.query.filter_by(username="test_notification_user").first()
            if test_user:
                # Delete in correct order: notifications -> items -> user
                Notification.query.filter_by(user_id=test_user.id).delete()
                Item.query.filter_by(user_id=test_user.id).delete()
                db.session.delete(test_user)
                db.session.commit()
            
            # Create test data
            print("\nCreating test data...")
            
            # Create a test user
            test_user = User()
            test_user.username = "test_notification_user"
            test_user.email = "test@example.com"
            test_user.password = "Test@123"
            test_user.is_verified = True
            
            # Create items with different expiry dates
            today = datetime.now().date()
            
            # 1. Item with 0 days left
            zero_days_item = Item()
            zero_days_item.name = "Zero Days Item"
            zero_days_item.description = "This item has 0 days left"
            zero_days_item.selling_price = 10.0
            zero_days_item.expiry_date = today
            zero_days_item.status = 'active'
            zero_days_item.user_id = None  # Will be set after user is created
            
            # 2. Item with 1 day left
            one_day_item = Item()
            one_day_item.name = "One Day Item"
            one_day_item.description = "This item has 1 day left"
            one_day_item.selling_price = 20.0
            one_day_item.expiry_date = today + timedelta(days=1)
            one_day_item.status = 'active'
            one_day_item.user_id = None  # Will be set after user is created
            
            # Add user to database
            db.session.add(test_user)
            db.session.commit()  # Commit to get user ID
            
            # Set user_id for items
            zero_days_item.user_id = test_user.id
            one_day_item.user_id = test_user.id
            
            # Add items to database
            db.session.add(zero_days_item)
            db.session.add(one_day_item)
            db.session.commit()  # Commit to get item IDs
            
            # Get IDs for verification
            zero_days_id = zero_days_item.id
            one_day_id = one_day_item.id
            
            print(f"Created test user with ID: {test_user.id}")
            print("Created 2 items (0 days left, 1 day left)")
            
            # Verify initial state
            print("\nVerifying initial state:")
            zero_days_exists = Item.query.get(zero_days_id) is not None
            one_day_exists = Item.query.get(one_day_id) is not None
            notifications_count = Notification.query.filter_by(user_id=test_user.id).count()
            
            print(f"Zero days item exists: {zero_days_exists}")
            print(f"One day item exists: {one_day_exists}")
            print(f"Initial notifications count: {notifications_count}")
            
            # Run cleanup task
            print("\nRunning cleanup task...")
            cleanup_expired_items()
            
            # Verify notifications
            print("\nVerifying notifications:")
            notifications = Notification.query.filter_by(user_id=test_user.id).all()
            print(f"Total notifications created: {len(notifications)}")
            
            for notification in notifications:
                print(f"\nNotification details:")
                print(f"- Message: {notification.message}")
                print(f"- Status: {notification.status}")
                print(f"- Priority: {notification.priority}")
                print(f"- Created: {notification.created_at}")
                print(f"- Item ID: {notification.item_id}")
            
            # Verify zero days item notification
            zero_days_notification = Notification.query.filter_by(
                user_id=test_user.id,
                item_id=zero_days_id
            ).first()
            
            if zero_days_notification:
                print("\n✅ Zero days item notification verified:")
                print(f"- Message contains '0 days left': {'0 days left' in zero_days_notification.message}")
                print(f"- Status is 'pending': {zero_days_notification.status == 'pending'}")
                print(f"- Priority is 'high': {zero_days_notification.priority == 'high'}")
            else:
                print("\n❌ Zero days item notification not found")
            
            # Clean up test data
            print("\nCleaning up test data...")
            Notification.query.filter_by(user_id=test_user.id).delete()
            Item.query.filter_by(user_id=test_user.id).delete()
            db.session.delete(test_user)
            db.session.commit()
            
            print("\n✅ Verification complete")
            
        except Exception as e:
            print(f"\n❌ Error during verification: {str(e)}")
            db.session.rollback()
        finally:
            # Final cleanup
            try:
                User.query.filter_by(username="test_notification_user").delete()
                db.session.commit()
            except:
                db.session.rollback()

if __name__ == "__main__":
    verify_notifications() 