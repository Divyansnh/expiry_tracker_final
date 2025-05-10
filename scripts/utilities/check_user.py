from app import create_app
from app.models.user import User
from app.core.extensions import db

app = create_app()

with app.app_context():
    # Search for user by username
    user = User.query.filter_by(username='Vedanshi').first()
    
    if user:
        print(f"\nUser found:")
        print(f"Username: {user.username}")
        print(f"Email: {user.email}")
        print(f"Created at: {user.created_at}")
        print(f"Is active: {user.is_active}")
        print(f"Is verified: {user.is_verified}")
    else:
        print("\nNo user found with username 'Vedanshi'")
        
    # Also check by email in case username is different
    user_by_email = User.query.filter_by(email='Vedanshi').first()
    if user_by_email:
        print(f"\nUser found by email:")
        print(f"Username: {user_by_email.username}")
        print(f"Email: {user_by_email.email}")
        print(f"Created at: {user_by_email.created_at}")
        print(f"Is active: {user_by_email.is_active}")
        print(f"Is verified: {user_by_email.is_verified}")
    else:
        print("\nNo user found with email 'Vedanshi'") 