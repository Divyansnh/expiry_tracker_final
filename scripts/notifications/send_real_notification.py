import os
import sys
from datetime import datetime

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.services.notification_service import NotificationService
from app.models.user import User
from app.models.item import Item
from app.core.extensions import db

def send_real_notification():
    """Send a real notification email with actual items."""
    print("\nStarting real notification test...")
    print("This will send an actual email to your registered email address.")
    
    # Create app with production config
    app = create_app('production')
    
    # Add necessary configuration for email template rendering
    app.config['SERVER_NAME'] = 'localhost:5000'
    app.config['APPLICATION_ROOT'] = '/'
    app.config['PREFERRED_URL_SCHEME'] = 'http'
    
    with app.app_context():
        try:
            # Get your user account
            user = User.query.filter_by(email='divyanshsingh1800@gmail.com').first()
            if not user:
                print("Error: User not found")
                return
            
            # Get all your items
            items = Item.query.filter_by(user_id=user.id).all()
            
            if not items:
                print("No items found for notification")
                return
            
            # Prepare items for notification with priorities
            notification_items = []
            for item in items:
                if item.expiry_date:
                    # Set priority based on days until expiry
                    if item.days_until_expiry <= 1:  # Today or tomorrow
                        priority = 'high'
                    elif item.days_until_expiry <= 7:  # Within 7 days
                        priority = 'normal'
                    else:  # More than 7 days
                        priority = 'low'
                    
                    notification_items.append({
                        'id': item.id,
                        'name': item.name,
                        'days_until_expiry': item.days_until_expiry,
                        'expiry_date': item.expiry_date,
                        'priority': priority
                    })
            
            print(f"\nFound {len(notification_items)} items to notify about")
            
            # Send notification
            notification_service = NotificationService()
            success = notification_service.send_daily_notification_email(user, notification_items)
            
            if success:
                print(f"\nNotification email sent successfully to {user.email}")
                print("Please check your inbox for the email")
            else:
                print("\nFailed to send notification email")
            
        except Exception as e:
            print(f"\nError during notification: {str(e)}")

if __name__ == '__main__':
    send_real_notification() 