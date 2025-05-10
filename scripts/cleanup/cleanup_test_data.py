import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.core.extensions import db

def cleanup_test_data():
    """Remove any test data from the actual database."""
    app = create_app()
    
    with app.app_context():
        print('=== Cleaning Up Test Data ===')
        
        # Remove test user
        test_user = User.query.filter_by(username='testuser', email='test@example.com').first()
        if test_user:
            print(f'\nRemoving test user: {test_user.username}')
            db.session.delete(test_user)
            db.session.commit()
            print('Test user removed successfully')
        else:
            print('\nNo test user found')

if __name__ == '__main__':
    cleanup_test_data() 