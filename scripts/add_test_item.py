from app import create_app
from app.models.item import Item
from app.models.user import User
from datetime import datetime, timedelta

def add_test_item():
    app = create_app()
    with app.app_context():
        # Get user 25
        user = User.query.get(25)
        if not user:
            print("User 25 not found")
            return
            
        # Create test item
        test_item = Item(
            name="Test Item for Ayush",
            description="This is a test item",
            expiry_date=datetime.now() + timedelta(days=3),  # Expires in 3 days
            status='active',
            user_id=user.id
        )
        
        # Add to database
        from app.core.extensions import db
        db.session.add(test_item)
        db.session.commit()
        
        print(f"Added test item for user {user.email}")
        print(f"Item name: {test_item.name}")
        print(f"Expiry date: {test_item.expiry_date}")

if __name__ == '__main__':
    add_test_item() 