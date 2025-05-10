from app import create_app
from app.models.notification import Notification
from datetime import datetime, timedelta

def check_notifications():
    app = create_app()
    with app.app_context():
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        
        # Get all notifications from yesterday onwards
        notifications = Notification.query.filter(
            Notification.created_at >= yesterday
        ).order_by(Notification.created_at.desc()).all()
        
        print(f'\nFound {len(notifications)} notifications from yesterday onwards:')
        for n in notifications:
            print(f'- {n.message}')
            print(f'  Status: {n.status}')
            print(f'  Created: {n.created_at}')
            print(f'  Type: {n.type}')
            print(f'  Priority: {n.priority}')
            print('---')

if __name__ == '__main__':
    check_notifications() 