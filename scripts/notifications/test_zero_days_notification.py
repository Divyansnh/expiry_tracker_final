import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from datetime import datetime, timedelta
from app import create_app
from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.tasks.cleanup import cleanup_expired_items
from app.core.extensions import db

def test_zero_days_notification():
    """Test notification creation for items with 0 days left."""
    app = create_app()
    with app.app_context():
        try:
            # Get the first user
            user = User.query.first()
            if not user:
                print("No user found in database")
                return

            # Create test item with 0 days left
            today = datetime.now().date()
            test_item = Item(
                name="Test Item - 0 Days Left",
                expiry_date=today,
                user_id=user.id,
                status='active'
            )
            
            # Add item to database
            db.session.add(test_item)
            db.session.commit()
            
            # Store ID for cleanup
            test_item_id = test_item.id
            
            print("\nCreated test item:")
            print(f"- Name: {test_item.name}")
            print(f"- Expiry Date: {test_item.expiry_date}")
            print(f"- Status: {test_item.status}")
            
            # Run cleanup to create notifications
            print("\nRunning cleanup task...")
            cleanup_expired_items()
            
            # Get notifications
            notifications = Notification.query.filter_by(
                user_id=user.id,
                item_id=test_item_id
            ).all()
            
            print("\nNotifications created:")
            for notification in notifications:
                print(f"- Message: {notification.message}")
                print(f"- Status: {notification.status}")
                print(f"- Priority: {notification.priority}")
                print(f"- Created: {notification.created_at}")
            
            # Verify notification was created
            if notifications:
                print("\n✅ Test passed: Notification was created for item with 0 days left")
            else:
                print("\n❌ Test failed: No notification was created")
            
            # Clean up
            print("\nCleaning up test data...")
            Notification.query.filter_by(item_id=test_item_id).delete()
            Item.query.filter_by(id=test_item_id).delete()
            db.session.commit()
            
        except Exception as e:
            print(f"\n❌ Error during test: {str(e)}")
            db.session.rollback()

if __name__ == "__main__":
    test_zero_days_notification() 