from app import create_app
from app.services.notification_service import NotificationService

def test_notifications():
    app = create_app()
    with app.app_context():
        service = NotificationService()
        service.check_expiry_dates()

if __name__ == '__main__':
    test_notifications() 