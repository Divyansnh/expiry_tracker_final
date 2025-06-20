from app import create_app
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime, timedelta

def update_notifications():
    app = create_app()
    with app.app_context():
        # Get the current user
        current_user = User.query.filter_by(email='divyanshsingh1800@gmail.com').first()
        if not current_user:
            print("User not found")
            return
            
        # Get today's notifications
        today = datetime.utcnow().date()
        notifications = Notification.query.filter(
            Notification.user_id == current_user.id,
            Notification.created_at >= today
        ).order_by(Notification.created_at.desc()).all()
        
        if not notifications:
            print("No notifications found for today")
            return
            
        print(f"\nFound {len(notifications)} notifications for today:")
        for n in notifications:
            print(f"Before: {n.message} (Status: {n.status}, Created: {n.created_at})")
            n.status = 'pending'
        
        # Commit the changes
        from app.core.extensions import db
        db.session.commit()
        
        print("\nUpdated notifications:")
        for n in notifications:
            print(f"After: {n.message} (Status: {n.status}, Created: {n.created_at})")

if __name__ == '__main__':
    update_notifications() 