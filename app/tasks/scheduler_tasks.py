from datetime import datetime
from flask import current_app
from app.tasks.cleanup import cleanup_expired_items, cleanup_unverified_accounts
from app.services.notification_service import NotificationService
from app import create_app

def cleanup_expired_task():
    """Task for cleaning up expired items."""
    app = create_app()
    with app.app_context():
        current_app.logger.info("Starting cleanup_expired_items job at %s", datetime.now())
        cleanup_expired_items()
        current_app.logger.info("Completed cleanup_expired_items job at %s", datetime.now())

def cleanup_unverified_task():
    """Task for cleaning up unverified accounts."""
    app = create_app()
    with app.app_context():
        current_app.logger.info("Starting cleanup_unverified_accounts job at %s", datetime.now())
        cleanup_unverified_accounts()
        current_app.logger.info("Completed cleanup_unverified_accounts job at %s", datetime.now())

def send_daily_notifications_task():
    """Task for sending daily notifications."""
    app = create_app()
    with app.app_context():
        current_app.logger.info("Starting send_daily_notifications job at %s", datetime.now())
        notification_service = NotificationService()
        notification_service.check_expiry_dates()
        current_app.logger.info("Completed send_daily_notifications job at %s", datetime.now()) 