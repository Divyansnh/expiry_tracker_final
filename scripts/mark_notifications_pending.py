import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app
from app.models.notification import Notification
from app.core.extensions import db

def mark_notifications_pending():
    app = create_app()
    with app.app_context():
        # Get the first 2 notifications
        notifications = Notification.query.order_by(Notification.created_at.desc()).limit(2).all()
        
        if not notifications:
            print("No notifications found")
            return
            
        # Mark them as pending
        for notification in notifications:
            notification.status = 'pending'
            print(f"Marking notification {notification.id} as pending")
            
        # Commit the changes
        db.session.commit()
        print(f"Successfully marked {len(notifications)} notifications as pending")

if __name__ == '__main__':
    mark_notifications_pending() 