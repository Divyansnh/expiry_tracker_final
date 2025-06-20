from app import create_app
from app.models.notification import Notification
from app.models.user import User
from datetime import datetime, timedelta
from sqlalchemy import and_

def update_notification_status():
    app = create_app()
    with app.app_context():
        # Get user Divyansh
        user = User.query.filter_by(email='divyanshsingh1800@gmail.com').first()
        if not user:
            print("User not found")
            return
            
        # Get today's date at midnight
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Find the most recent daily notification for today
        notification = Notification.query.filter(
            and_(
                Notification.user_id == user.id,
                Notification.created_at >= today_start,
                Notification.type == 'email',
                Notification.message.like('Daily status update sent for% items%')
            )
        ).order_by(Notification.created_at.desc()).first()
        
        if notification:
            # Update status to pending
            notification.status = 'pending'
            notification.save()
            print(f"Updated notification {notification.id} to pending status")
            print(f"Created at: {notification.created_at}")
            print(f"Message: {notification.message}")
        else:
            print("No daily notification found for today")

if __name__ == '__main__':
    update_notification_status() 