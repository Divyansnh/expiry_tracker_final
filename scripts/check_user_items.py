from app import create_app
from app.models.item import Item
from app.models.user import User

def check_user_items():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        print('\nItems by User:')
        for user in users:
            print(f'\nUser {user.email} (ID: {user.id}):')
            items = Item.query.filter_by(user_id=user.id).all()
            print(f'Found {len(items)} items')
            for item in items:
                print(f'- {item.name} (ID: {item.id}, Expiry: {item.expiry_date}, Status: {item.status})')

if __name__ == '__main__':
    check_user_items() 