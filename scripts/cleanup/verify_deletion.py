import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User

app = create_app()

with app.app_context():
    # Check by username
    user1 = User.query.filter_by(username='Vedanshi@2102').first()
    # Check by email
    user2 = User.query.filter_by(email='singhdivyansh919@gmail.com').first()
    
    if user1 is None and user2 is None:
        print("Verification successful: User has been completely removed from the system.")
    else:
        print("Warning: User still exists in the system!") 