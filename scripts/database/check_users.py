import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.core.extensions import db

app = create_app()

with app.app_context():
    try:
        # Get all users
        users = User.query.all()
        
        print(f"\nTotal users in database: {len(users)}")
        print("\nUser details:")
        for user in users:
            print(f"Username: {user.username}")
            print(f"Email: {user.email}")
            print(f"Verified: {user.is_verified}")
            print(f"Created at: {user.created_at}")
            print("-" * 50)
            
    except Exception as e:
        print(f"Error querying database: {str(e)}")
        db.session.rollback() 