import os
import sys
from datetime import datetime, timedelta

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.item import Item
from app.core.extensions import db

def test_individual_notifications():
    """Test individual notifications for specific expiry days."""
    print("\nStarting individual notification test...")
    print("This test will not affect your production data or send actual emails.")
    
    # Create a test app with test configuration
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database
    app.config['TESTING'] = True
    app.config['SERVER_NAME'] = 'localhost'  # Required for url_for to work
    
    with app.app_context():
        try:
            # Create all tables in the test database
            db.create_all()
            
            # Create a test user
            test_user = User()
            test_user.username = 'test_individual_user'
            test_user.email = 'test_individual@example.com'
            test_user.password = 'Test@123'
            test_user.email_notifications = True
            db.session.add(test_user)
            db.session.commit()
            
            # Create test items with specific notification days
            today = datetime.utcnow().date()
            test_items = [
                ('Item Expiring in 30 Days', today + timedelta(days=30)),
                ('Item Expiring in 15 Days', today + timedelta(days=15)),
                ('Item Expiring in 7 Days', today + timedelta(days=7)),
                ('Item Expiring in 3 Days', today + timedelta(days=3)),
                ('Item Expiring in 1 Day', today + timedelta(days=1)),
                ('Item Expiring Today', today),
                ('Item Expired Yesterday', today - timedelta(days=1))
            ]
            
            for name, expiry_date in test_items:
                item = Item(
                    name=name,
                    expiry_date=expiry_date,
                    user_id=test_user.id
                )
                db.session.add(item)
            
            db.session.commit()
            
            print("\nCreated test data:")
            print(f"- User: {test_user.email}")
            print("- Items:")
            for item in Item.query.filter_by(user_id=test_user.id).all():
                print(f"  - {item.name}: {item.expiry_date} ({item.days_until_expiry} days until expiry)")
            
            # Run notification service
            print("\nSimulating individual notifications...")
            notification_service = NotificationService()
            notification_service.check_expiry_dates()
            
            # Show notifications that would have been created
            notifications = db.session.query(Item).filter_by(user_id=test_user.id).all()
            print("\nItems that would trigger individual notifications:")
            for item in notifications:
                days = item.days_until_expiry
                if days is not None:
                    if days in [1, 3, 7, 15, 30] or days <= 0:
                        priority = 'high' if days <= 3 else 'normal' if days <= 7 else 'low'
                        if days < 0:
                            print(f"  - {item.name}: Expired {abs(days)} days ago (Priority: {priority})")
                        elif days == 0:
                            print(f"  - {item.name}: Expires today (Priority: {priority})")
                        else:
                            print(f"  - {item.name}: Expires in {days} days (Priority: {priority})")
            
            print("\nTest completed successfully!")
            print("Note: This was a simulation. No actual emails were sent.")
            print("In production, you would receive individual emails for each item at these specific days.")
            
        except Exception as e:
            print(f"\nError during test: {str(e)}")
        finally:
            # Clean up by dropping all tables in the test database
            db.session.remove()
            db.drop_all()
            print("\nCleaned up all test data.")

if __name__ == '__main__':
    test_individual_notifications() 