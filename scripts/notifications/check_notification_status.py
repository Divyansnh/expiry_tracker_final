from app import create_app
from app.models.notification import Notification
from app.core.extensions import db
from datetime import datetime, timedelta

def check_notification_status():
    app = create_app()
    with app.app_context():
        # Get total notifications
        total = Notification.query.count()
        print(f"\nTotal notifications: {total}")
        
        # Get notifications with NULL status
        null_status = Notification.query.filter(Notification.status == None).count()
        print(f"Notifications with NULL status: {null_status}")
        
        # Get notifications by status
        pending = Notification.query.filter_by(status='pending').count()
        sent = Notification.query.filter_by(status='sent').count()
        print(f"Pending notifications: {pending}")
        print(f"Sent notifications: {sent}")

        # Get all notifications
        print("\nAll Notifications (newest to oldest):")
        print("=" * 100)
        all_notifications = Notification.query.order_by(
            Notification.created_at.desc()
        ).all()
        
        for notification in all_notifications:
            print(f"ID: {notification.id}")
            print(f"Message: {notification.message}")
            print(f"Status: {notification.status}")
            print(f"Created At: {notification.created_at}")
            print(f"Type: {notification.type}")
            if notification.item_id:
                print(f"Item ID: {notification.item_id}")
            print("-" * 100)

if __name__ == '__main__':
    check_notification_status() 