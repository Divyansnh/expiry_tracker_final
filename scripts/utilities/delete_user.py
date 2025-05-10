from app import create_app, db
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.models.report import Report

app = create_app()

with app.app_context():
    try:
        # Find the user
        user = User.query.filter_by(username='Vedanshi').first()
        
        if user:
            print(f"Found user: {user.username} ({user.email})")
            
            # Delete associated items
            items = Item.query.filter_by(user_id=user.id).all()
            for item in items:
                db.session.delete(item)
            print(f"Deleted {len(items)} items")
            
            # Delete associated notifications
            notifications = Notification.query.filter_by(user_id=user.id).all()
            for notification in notifications:
                db.session.delete(notification)
            print(f"Deleted {len(notifications)} notifications")
            
            # Delete associated reports
            reports = Report.query.filter_by(user_id=user.id).all()
            for report in reports:
                db.session.delete(report)
            print(f"Deleted {len(reports)} reports")
            
            # Finally, delete the user
            db.session.delete(user)
            db.session.commit()
            
            print("User and all associated data have been deleted successfully.")
        else:
            print("User Vedanshi not found.")
            
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting user: {str(e)}") 