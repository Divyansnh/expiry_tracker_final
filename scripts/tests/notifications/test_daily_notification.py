import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.insert(0, project_root)

from app import create_app
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.item import Item
from app.core.extensions import db

def test_daily_notification():
    """Test the daily notification service."""
    print("\nStarting daily notification test...")
    
    # Create a test app with test configuration
    app = create_app('testing')
    
    with app.app_context():
        try:
            # Create a test user
            test_user = User()
            test_user.username = 'test_notification_user'
            test_user.email = 'test_notification@example.com'
            test_user.password = 'Test@123'  # This will trigger the password setter
            test_user.email_notifications = True
            db.session.add(test_user)
            db.session.commit()
            
            # Create test items with different expiry dates
            today = datetime.utcnow().date()
            test_items = [
                ('Test Item Expired', today - timedelta(days=1), 'expired'),
                ('Test Item Expiring Today', today, 'expiring_soon'),
                ('Test Item Expiring in 3 Days', today + timedelta(days=3), 'expiring_soon'),
                ('Test Item Expiring in 7 Days', today + timedelta(days=7), 'expiring_soon'),
                ('Test Item Active', today + timedelta(days=30), 'active')
            ]
            
            for name, expiry_date, status in test_items:
                item = Item(
                    name=name,
                    expiry_date=expiry_date,
                    status=status,
                    user_id=test_user.id
                )
                db.session.add(item)
            
            db.session.commit()
            
            print("\nCreated test data:")
            print(f"- User: {test_user.email}")
            print("- Items:")
            for item in Item.query.filter_by(user_id=test_user.id).all():
                print(f"  - {item.name}: {item.expiry_date} ({item.status})")
            
            # Run notification service
            print("\nRunning notification service...")
            notification_service = NotificationService()
            notification_service.check_expiry_dates()
            
            print("\nTest completed successfully!")
            print("Note: This was a test run. No actual emails were sent.")
            print("To see actual emails, check your email inbox at 6:00 AM BST.")
            
        except Exception as e:
            print(f"\nError during test: {str(e)}")
        finally:
            # Clean up test data
            try:
                test_user = User.query.filter_by(email='test_notification@example.com').first()
                if test_user:
                    Item.query.filter_by(user_id=test_user.id).delete()
                    db.session.delete(test_user)
                    db.session.commit()
            except:
                db.session.rollback()

if __name__ == '__main__':
    test_daily_notification() 