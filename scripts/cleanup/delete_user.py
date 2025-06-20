import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.models.user import User
from app.models.notification import Notification
from app.models.item import Item
from app.models.report import Report
from app.core.extensions import db

def delete_user_by_email(email):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email=email).first()
        if user:
            # Delete related notifications
            Notification.query.filter_by(user_id=user.id).delete()
            # Delete related items
            Item.query.filter_by(user_id=user.id).delete()
            # Delete related reports
            Report.query.filter_by(user_id=user.id).delete()
            db.session.delete(user)
            db.session.commit()
            print(f"User with email {email} and all related data deleted successfully.")
        else:
            print(f"User with email {email} not found.")

if __name__ == "__main__":
    delete_user_by_email('singhdivyansh919@gmail.com') 