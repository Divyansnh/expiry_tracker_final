from app import create_app
from app.services.notification_service import NotificationService
from app.models.user import User

def trigger_notification_check():
    app = create_app()
    with app.app_context():
        print("Starting notification check...")
        notification_service = NotificationService()
        
        # Get all users with email notifications enabled
        users = User.query.filter_by(email_notifications=True).all()
        print(f"\nFound {len(users)} users with email notifications enabled:")
        for user in users:
            print(f"- User {user.id}: {user.email}")
        
        print("\nProcessing notifications for each user...")
        for user in users:
            print(f"\nProcessing user {user.id} ({user.email})...")
            notification_service.check_expiry_dates(user.id)

if __name__ == '__main__':
    trigger_notification_check() 