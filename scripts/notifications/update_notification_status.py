from app import create_app
from app.models.notification import Notification
from app.core.extensions import db

def update_recent_notifications():
    app = create_app()
    with app.app_context():
        # Get the two most recent notifications
        recent_notifications = Notification.query.order_by(
            Notification.created_at.desc()
        ).limit(2).all()
        
        print("\nUpdating notification statuses:")
        print("-" * 80)
        
        for notification in recent_notifications:
            print(f"Before update:")
            print(f"Message: {notification.message}")
            print(f"Old Status: {notification.status}")
            print(f"Created At: {notification.created_at}")
            
            # Update status to pending
            notification.status = 'pending'
            
            print(f"\nAfter update:")
            print(f"New Status: {notification.status}")
            print("-" * 80)
        
        # Commit the changes
        try:
            db.session.commit()
            print("\nSuccessfully updated notification statuses to pending!")
        except Exception as e:
            db.session.rollback()
            print(f"\nError updating notifications: {str(e)}")

if __name__ == '__main__':
    update_recent_notifications() 