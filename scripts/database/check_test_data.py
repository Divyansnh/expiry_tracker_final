import os
import sys
from sqlalchemy import text

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.models.item import Item
from app.models.user import User
from app.models.notification import Notification

def check_test_data():
    """Check for test data in the database."""
    app = create_app()
    with app.app_context():
        print("\nChecking for test data...")
        
        # Check test users
        test_users = User.query.filter(text("username LIKE 'test%'")).all()
        print("\nTest Users:")
        for user in test_users:
            print(f"- {user.username} (ID: {user.id})")
        
        # Check test items
        test_items = Item.query.filter(text("name LIKE 'Test%'")).all()
        print("\nTest Items:")
        for item in test_items:
            print(f"- {item.name} (ID: {item.id}, User: {item.user_id})")
        
        # Check test notifications
        test_notifications = Notification.query.filter(text("message LIKE 'Test%'")).all()
        print("\nTest Notifications:")
        for notification in test_notifications:
            print(f"- {notification.message} (ID: {notification.id}, User: {notification.user_id})")
        
        print("\nCheck complete!")

if __name__ == "__main__":
    check_test_data() 