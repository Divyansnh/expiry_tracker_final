import os
import sys
from datetime import datetime, timedelta
import time

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from app import create_app
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.core.extensions import db
from app.tasks.cleanup import cleanup_unverified_accounts
from app.core.config import Config

class TestConfig(Config):
    """Test configuration."""
    SCHEDULER_API_ENABLED = False

# Create a single app instance for all tests
app = create_app(TestConfig)

def setup_test():
    """Create test data and return the test users."""
    with app.app_context():
        # Create verified user (should not be deleted)
        verified_user = User()
        verified_user.username = 'verified_user'
        verified_user.email = 'verified@example.com'
        verified_user.password = 'Test@123'  # Strong password
        verified_user.is_verified = True
        verified_user.save()
        
        # Create unverified user (should be deleted)
        unverified_user = User()
        unverified_user.username = 'unverified_user'
        unverified_user.email = 'unverified@example.com'
        unverified_user.password = 'Test@123'  # Strong password
        unverified_user.is_verified = False
        unverified_user.created_at = datetime.now() - timedelta(hours=2)  # 2 hours old
        unverified_user.save()
        
        # Create recent unverified user (should not be deleted)
        recent_user = User()
        recent_user.username = 'recent_user'
        recent_user.email = 'recent@example.com'
        recent_user.password = 'Test@123'  # Strong password
        recent_user.is_verified = False
        recent_user.created_at = datetime.now() - timedelta(minutes=30)  # 30 minutes old
        recent_user.save()
        
        # Create items for unverified user
        item1 = Item()
        item1.name = 'Test Item 1'
        item1.user_id = unverified_user.id
        db.session.add(item1)
        
        item2 = Item()
        item2.name = 'Test Item 2'
        item2.user_id = unverified_user.id
        db.session.add(item2)
        
        # Create notifications for unverified user
        notification1 = Notification()
        notification1.user_id = unverified_user.id
        notification1.message = 'Test notification 1'
        db.session.add(notification1)
        
        notification2 = Notification()
        notification2.user_id = unverified_user.id
        notification2.message = 'Test notification 2'
        db.session.add(notification2)
        
        db.session.commit()
        
        print("\nTest data created:")
        print(f"1. Verified user: {verified_user.username}")
        print(f"2. Unverified user (2 hours old): {unverified_user.username}")
        print(f"3. Recent unverified user (30 minutes old): {recent_user.username}")
        print(f"4. Items for unverified user: 2")
        print(f"5. Notifications for unverified user: 2")
        
        return {
            'verified_id': verified_user.id,
            'unverified_id': unverified_user.id,
            'recent_id': recent_user.id
        }

def verify_cleanup(user_ids):
    """Run cleanup and verify results."""
    with app.app_context():
        # Get initial counts
        initial_users = User.query.count()
        initial_unverified = User.query.filter_by(is_verified=False).count()
        initial_items = Item.query.count()
        initial_notifications = Notification.query.count()
        
        print(f"\nBefore cleanup:")
        print(f"Total users: {initial_users}")
        print(f"Unverified users: {initial_unverified}")
        print(f"Total items: {initial_items}")
        print(f"Total notifications: {initial_notifications}")
        
        # Run cleanup
        print("\nRunning cleanup...")
        deleted_count = cleanup_unverified_accounts()
        
        # Get final counts
        final_users = User.query.count()
        final_unverified = User.query.filter_by(is_verified=False).count()
        final_items = Item.query.count()
        final_notifications = Notification.query.count()
        
        print(f"\nAfter cleanup:")
        print(f"Total users: {final_users}")
        print(f"Unverified users: {final_unverified}")
        print(f"Total items: {final_items}")
        print(f"Total notifications: {final_notifications}")
        print(f"Deleted accounts: {deleted_count}")
        
        # Verify specific users
        verified_exists = User.query.get(user_ids['verified_id']) is not None
        unverified_exists = User.query.get(user_ids['unverified_id']) is not None
        recent_exists = User.query.get(user_ids['recent_id']) is not None
        
        print("\nUser status:")
        print(f"Verified user exists: {verified_exists}")
        print(f"Old unverified user exists: {unverified_exists}")
        print(f"Recent unverified user exists: {recent_exists}")
        
        # Verify cleanup results
        success = (
            verified_exists and  # Verified user should still exist
            not unverified_exists and  # Old unverified user should be deleted
            recent_exists and  # Recent unverified user should still exist
            final_items == initial_items - 2 and  # 2 items should be deleted
            final_notifications == initial_notifications - 2  # 2 notifications should be deleted
        )
        
        if success:
            print("\n✅ Cleanup successful! All verifications passed.")
        else:
            print("\n❌ Cleanup failed! Some verifications did not pass.")

def cleanup_test_data(user_ids):
    """Clean up all test data."""
    with app.app_context():
        try:
            # Delete all test users
            User.query.filter(User.id.in_(user_ids.values())).delete(synchronize_session=False)
            
            # Delete all items and notifications (should be handled by cascade)
            db.session.commit()
            print("\nTest data cleaned up successfully!")
        except Exception as e:
            print(f"Error cleaning up test data: {str(e)}")
            db.session.rollback()

if __name__ == '__main__':
    print("Starting unverified accounts cleanup test...")
    
    # Setup test data
    user_ids = setup_test()
    
    # Run and verify cleanup
    verify_cleanup(user_ids)
    
    # Clean up test data
    cleanup_test_data(user_ids)
    
    print("\nTest completed!") 