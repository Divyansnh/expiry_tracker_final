from app import create_app
from app.models.user import User
from app.core.extensions import db

app = create_app()

with app.app_context():
    user = User.query.filter_by(username='Vedanshi').first()
    if user:
        db.session.delete(user)
        db.session.commit()
        print(f"User {user.username} has been deleted successfully")
    else:
        print("User not found") 