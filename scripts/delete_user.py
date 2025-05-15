import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from app import create_app
from app.models.user import User
from app.models.report import Report
from app.core.extensions import db

def delete_user(username):
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        if user:
            # Delete all reports associated with the user
            Report.query.filter_by(user_id=user.id).delete()
            db.session.commit()
            print(f"All reports for user '{username}' have been deleted.")

            # Now delete the user
            db.session.delete(user)
            db.session.commit()
            print(f"User '{username}' has been deleted from the database.")
        else:
            print(f"User '{username}' not found in the database.")

if __name__ == '__main__':
    delete_user('Vedanshi') 