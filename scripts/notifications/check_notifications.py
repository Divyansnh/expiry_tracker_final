from app import create_app
from app.models.notification import Notification
from app.models.user import User
from app.core.extensions import db
from datetime import datetime, timedelta

def check_notifications():
    app = create_app()
    with app.app_context():
        # Get the current user
        current_user = User.query.filter_by(email='divyanshsingh1800@gmail.com').first()
        if not current_user:
            print("User not found")
            return
            
        print("\n=== Your Notifications ===")
        
        # Get all notifications for the user
        notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
        
        if not notifications:
            print("No notifications found")
            return
            
        print(f"\nFound {len(notifications)} notifications:")
        for n in notifications:
            print(f"- {n.message} (Status: {n.status}, Created: {n.created_at})")

def check_recent_notifications():
    app = create_app()
    with app.app_context():
        # Get notifications from the last 24 hours
        recent_notifications = Notification.query.filter(
            Notification.created_at >= datetime.utcnow() - timedelta(hours=24)
        ).order_by(Notification.created_at.desc()).all()
        
        print("\nRecent Notifications (last 24 hours):")
        print("=" * 80)
        for notification in recent_notifications:
            print(f"ID: {notification.id}")
            print(f"User ID: {notification.user_id}")
            print(f"Message: {notification.message}")
            print(f"Status: {notification.status}")
            print(f"Created At: {notification.created_at}")
            print("-" * 80)

if __name__ == '__main__':
    check_notifications()
    check_recent_notifications() 