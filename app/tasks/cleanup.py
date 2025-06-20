from datetime import datetime, timedelta
from app.core.extensions import db
from app.models.item import Item
from app.models.notification import Notification
from app.models.user import User
from app.services.zoho_service import ZohoService
from app.services.notification_service import NotificationService
from flask import current_app
from sqlalchemy.sql import func

def cleanup_expired_items():
    """Cleanup expired items and send notifications."""
    try:
        current_date = datetime.now().date()
        
        # First, update all item statuses to ensure consistency
        items = Item.query.all()
        for item in items:
            item.update_status(force_update=True)
        db.session.commit()
        
        # Find items with 0 days left
        items_zero_days = Item.query.filter(
            Item.expiry_date == current_date,
            func.lower(Item.status) != 'expired'
        ).all()
        
        # Find all expired items (case-insensitive)
        expired_items = Item.query.filter(
            Item.expiry_date < current_date,
            func.lower(Item.status) == 'expired'
        ).all()
        
        notification_service = NotificationService()
        
        # Create notifications for items with 0 days left
        for item in items_zero_days:
            notification_service.create_notification(
                user_id=item.user_id,
                item_id=item.id,
                message=f"Item '{item.name}' (ID: {item.id}) has 0 days left and is expiring soon.",
                type='email',
                priority='high',
                status='pending'  # Set as pending to show in notifications page
            )
        
        for item in expired_items:
            # Create notification for the user
            notification_service.create_notification(
                user_id=item.user_id,
                item_id=item.id,
                message=f"Item '{item.name}' (ID: {item.id}) has expired and will be removed from the system.",
                type='email',
                priority='high',
                status='pending'  # Set as pending to show in notifications page
            )
            
            # Mark item as inactive in Zoho if it has a Zoho ID
            if item.zoho_item_id:
                try:
                    # Get the user associated with the item
                    user = item.user
                    if user:
                        zoho_service = ZohoService(user)
                        zoho_service.delete_item_in_zoho(item.zoho_item_id)
                except Exception as e:
                    current_app.logger.error(f"Error deleting item from Zoho: {str(e)}")
            
            # Remove item from database
            db.session.delete(item)
        
        db.session.commit()
        current_app.logger.info(f"Successfully cleaned up {len(expired_items)} expired items")
        current_app.logger.info(f"Created notifications for {len(items_zero_days)} items with 0 days left")
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up expired items: {str(e)}")
        db.session.rollback()

def cleanup_unverified_accounts():
    """Cleanup unverified user accounts that are older than 1 hour."""
    try:
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        
        # Find unverified accounts older than 1 hour
        unverified_users = User.query.filter_by(
            is_verified=False
        ).filter(
            User.created_at <= one_hour_ago
        ).all()
        
        deleted_count = 0
        for user in unverified_users:
            try:
                # Delete all items associated with the user
                Item.query.filter_by(user_id=user.id).delete(synchronize_session=False)
                
                # Delete all notifications associated with the user
                Notification.query.filter_by(user_id=user.id).delete(synchronize_session=False)
                
                # Delete the user
                db.session.delete(user)
                deleted_count += 1
                
            except Exception as e:
                current_app.logger.error(f"Error deleting user {user.id}: {str(e)}")
                db.session.rollback()
                continue
        
        db.session.commit()
        current_app.logger.info(f"Successfully cleaned up {deleted_count} unverified accounts")
        return deleted_count
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up unverified accounts: {str(e)}")
        db.session.rollback()
        return 0 