from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict, Any, Literal, TypedDict, Sequence, cast
from flask import current_app
from app.core.extensions import db
from app.models.notification import Notification
from app.models.item import Item, STATUS_EXPIRED
from app.models.user import User
from app.services.email_service import EmailService
from sqlalchemy import and_, not_, or_
from sqlalchemy.sql import expression
from sqlalchemy.sql.expression import BinaryExpression, ColumnElement

class ItemNotification(TypedDict):
    name: str
    days_until_expiry: int
    priority: Literal['high', 'normal', 'low']

NotificationType = Literal['email']
NotificationPriority = Literal['high', 'normal', 'low']

class NotificationService:
    """Service for handling expiry notifications."""
    
    def __init__(self) -> None:
        self._notification_days: Optional[List[int]] = None
        self.email_service = EmailService()
    
    @property
    def notification_days(self) -> List[int]:
        """Get notification days from config."""
        if self._notification_days is None:
            config_days = current_app.config.get('NOTIFICATION_DAYS')
            if config_days is None:
                self._notification_days = []
            else:
                self._notification_days = list(config_days)  # Ensure it's a list
        return self._notification_days
    
    def check_expiry_dates(self) -> None:
        """Check all items for expiry dates and send email notifications."""
        try:
            current_app.logger.info("Starting expiry date check at %s", datetime.now())
            
            # Get all items with expiry dates that are not already expired
            items = Item.query.filter(
                and_(
                    cast(BinaryExpression, Item.expiry_date.isnot(None)),
                    cast(BinaryExpression, Item.status != STATUS_EXPIRED)
                )
            ).all()
            
            current_app.logger.info("Found %d items to check for notifications", len(items))
            
            # Group items by user
            user_items: Dict[int, List[Dict[str, Any]]] = {}
            
            for item in items:
                days_until_expiry = item.days_until_expiry
                if days_until_expiry is None:
                    current_app.logger.debug(f"Skipping item {item.id} - No expiry date")
                    continue
                    
                # Process all items for daily notification
                if item.user_id not in user_items:
                    user_items[item.user_id] = []
                
                # Set priority based on days until expiry
                if days_until_expiry <= 3:
                    priority = 'high'
                elif days_until_expiry <= 7:
                    priority = 'normal'
                else:
                    priority = 'low'
                
                user_items[item.user_id].append({
                    'id': item.id,
                    'name': item.name,
                    'days_until_expiry': days_until_expiry,
                    'expiry_date': item.expiry_date,
                    'priority': priority
                })
                current_app.logger.debug(f"Added item {item.id} ({item.name}) to notifications - Days until expiry: {days_until_expiry}, Priority: {priority}")
            
            # Send email notifications to each user
            for user_id, items in user_items.items():
                user = User.query.get(user_id)
                current_app.logger.info(f"Processing notifications for user {user_id}")
                
                if not user:
                    current_app.logger.warning(f"User {user_id} not found")
                    continue
                    
                if not user.email:
                    current_app.logger.warning(f"User {user_id} has no email address")
                    continue
                    
                if not user.email_notifications:
                    current_app.logger.info(f"User {user_id} ({user.email}) has disabled email notifications")
                    continue
                
                current_app.logger.info(f"Attempting to send notification to user {user.username} ({user.email}) for {len(items)} items")
                self.send_daily_notification_email(user, items)
            
            current_app.logger.info("Completed expiry date check at %s", datetime.now())
            
        except Exception as e:
            current_app.logger.error(f"Error checking expiry dates: {str(e)}")
            raise
    
    def send_daily_notification_email(self, user: User, items: List[Dict[str, Any]]) -> bool:
        """Send a daily notification email to a user about their items."""
        try:
            if not items:
                current_app.logger.info(f"No items to notify about for user {user.email}")
                return False
                
            # Sort items by days until expiry
            items.sort(key=lambda x: x['days_until_expiry'])
            
            # Check if notification already sent today
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            existing_notification = Notification.query.filter(
                and_(
                    cast(ColumnElement[bool], Notification.user_id == user.id),
                    cast(ColumnElement[bool], Notification.created_at >= today_start),
                    cast(ColumnElement[bool], Notification.type == 'email'),
                    cast(ColumnElement[bool], Notification.status == 'sent')
                )
            ).first()
            
            if existing_notification:
                current_app.logger.info(f"Daily notification already sent to {user.email} today at {existing_notification.created_at}")
                return True
            
            current_app.logger.info(f"Preparing to send notification email to {user.email} for {len(items)} items")
            
            # Prepare email content
            subject = "Expiry Tracker - Daily Item Status Update"
            template = 'daily_notification'
            
            # Send email
            result = self.email_service.send_email(
                subject=subject,
                recipients=[str(user.email)],
                template=template,
                user=user,
                items=items
            )
            
            if result:
                current_app.logger.info(f"Successfully sent notification email to {user.email}")
                # Create notification record
                notification = self.create_notification(
                    user_id=user.id,
                    item_id=items[0]['id'],
                    message=f"Daily status update sent for {len(items)} items",
                    type='email',
                    priority='normal',
                    status='pending'  # Create as pending so user can mark it as sent
                )
                if notification:
                    current_app.logger.info(f"Created notification record {notification.id} for user {user.email}")
                else:
                    current_app.logger.error(f"Failed to create notification record for user {user.email}")
            else:
                current_app.logger.error(f"Failed to send notification email to {user.email}")
            
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error sending daily notification email to {user.email}: {str(e)}")
            return False
    
    def create_notification(
        self,
        user_id: int,
        item_id: int,
        message: str,
        type: NotificationType,
        priority: NotificationPriority = 'normal',
        status: Literal['sent', 'pending'] = 'pending'
    ) -> Optional[Notification]:
        """Create a new notification record.
        
        Args:
            user_id: ID of the user to notify
            item_id: ID of the item this notification is about
            message: The notification message
            type: Type of notification (email)
            priority: Priority level of the notification
            status: Status of the notification (sent or pending)
            
        Returns:
            The created notification or None if creation failed
        """
        notification = Notification()
        notification.user_id = user_id
        notification.item_id = item_id
        notification.message = message
        notification.type = type
        notification.priority = priority
        notification.status = status
        
        try:
            db.session.add(notification)
            db.session.commit()
            return notification
        except Exception as e:
            current_app.logger.error(f"Error creating notification: {str(e)}")
            db.session.rollback()
            return None
    
    def get_user_notifications(self, user_id: int, limit: int = 10, show_sent: bool = False) -> List[Notification]:
        """Get notifications for a specific user.
        
        Args:
            user_id: The ID of the user to get notifications for
            limit: Maximum number of notifications to return
            show_sent: Whether to include sent notifications
            
        Returns:
            List of Notification objects
        """
        try:
            query = Notification.query.filter_by(
                user_id=user_id,
                type='email'
            )
            
            if not show_sent:
                query = query.filter_by(status='pending')
                
            notifications = query.order_by(
                Notification.created_at.desc()
            ).limit(limit).all()
            
            return notifications
        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return [] 