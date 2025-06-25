from datetime import datetime, timedelta
from typing import List, Optional, Union, Dict, Any, Literal, TypedDict, Sequence, cast
from flask import current_app
from app.core.extensions import db
from app.models.notification import Notification
from app.models.item import Item, STATUS_EXPIRED
from app.models.user import User
from app.services.email_service import EmailService
from app.services.activity_service import ActivityService
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
        self.activity_service = ActivityService()
    
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
    
    def check_expiry_dates(self, user_id: Optional[int] = None) -> None:
        """Check all items for expiry dates and send email notifications."""
        try:
            current_app.logger.info("Starting expiry date check at %s", datetime.now())
            
            # Get all items with expiry dates that are not already expired
            query = Item.query.filter(
                and_(
                    cast(BinaryExpression, Item.expiry_date.isnot(None)),
                    cast(BinaryExpression, Item.status != STATUS_EXPIRED)
                )
            )
            
            # If user_id is provided, only get items for that user
            if user_id is not None:
                query = query.filter_by(user_id=user_id)
            
            items = query.all()
            
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
                if days_until_expiry <= 1:  # Today or tomorrow
                    priority = 'high'
                    # Log expiry alert for urgent items
                    self.activity_service.log_expiry_alert(item.user_id, item.name, days_until_expiry)
                elif 2 <= days_until_expiry <= 7:  # 2-7 days
                    priority = 'normal'
                    # Log expiry alert for items expiring soon
                    self.activity_service.log_expiry_alert(item.user_id, item.name, days_until_expiry)
                else:  # 8+ days
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
                    cast(ColumnElement[bool], Notification.status == 'sent'),
                    cast(ColumnElement[bool], Notification.message.like('Daily status update sent for% items%'))
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
                
                # Log activity for notification sent
                self.activity_service.log_notification_sent(
                    user_id=user.id,
                    notification_type="Daily status update",
                    item_count=len(items)
                )
                
                # Create notification record
                notification = self.create_notification(
                    user_id=user.id,
                    item_id=items[0]['id'],
                    message=f"Daily status update sent for {len(items)} items to {user.email}",
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
                type='email',
                status='sent' if show_sent else 'pending'
            )
                
            notifications = query.order_by(
                Notification.created_at.desc()
            ).limit(limit).all()
            
            return notifications
        except Exception as e:
            current_app.logger.error(f"Error getting user notifications: {str(e)}")
            return []
    
    def get_user_notifications_all(self, user_id: int, limit: int = 10) -> List[Notification]:
        """Get all notifications (both sent and pending) for a specific user.
        
        Args:
            user_id: The ID of the user to get notifications for
            limit: Maximum number of notifications to return
            
        Returns:
            List of Notification objects
        """
        try:
            query = Notification.query.filter_by(
                user_id=user_id,
                type='email'
            )
                
            notifications = query.order_by(
                Notification.created_at.desc()
            ).limit(limit).all()
            
            return notifications
        except Exception as e:
            current_app.logger.error(f"Error getting all user notifications: {str(e)}")
            return []
    
    def get_notification_count(self, user_id: int, status: Optional[str] = None) -> int:
        """Get the count of notifications for a specific user.
        
        Args:
            user_id: The ID of the user to get notification count for
            status: Status filter ('sent', 'pending', or None for all)
            
        Returns:
            Count of notifications
        """
        try:
            query = Notification.query.filter_by(
                user_id=user_id,
                type='email'
            )
            
            if status:
                query = query.filter_by(status=status)
                
            return query.count()
        except Exception as e:
            current_app.logger.error(f"Error getting notification count: {str(e)}")
            return 0
    
    def get_user_notifications_paginated(self, user_id: int, page: int = 1, per_page: int = 20, show_sent: bool = False, search: Optional[str] = None, search_mode: str = 'message') -> tuple[List[Notification], int]:
        """Get paginated notifications for a specific user.
        
        Args:
            user_id: The ID of the user to get notifications for
            page: Page number (1-based)
            per_page: Number of notifications per page
            show_sent: Whether to include sent notifications
            search: Optional search term to filter notifications
            search_mode: Search mode ('message', 'item', 'email', 'date')
            
        Returns:
            Tuple of (notifications, total_count)
        """
        try:
            query = Notification.query.filter_by(
                user_id=user_id,
                type='email',
                status='sent' if show_sent else 'pending'
            )
            
            # Add search filter based on mode
            if search:
                if search_mode == 'message':
                    query = query.filter(Notification.message.ilike(f'%{search}%'))
                elif search_mode == 'date':
                    # Search by date in created_at only (not message content)
                    try:
                        if len(search) == 4 and search.isdigit():  # Year only
                            year = int(search)
                            if 1900 <= year <= 2100:
                                query = query.filter(
                                    Notification.created_at >= datetime(year, 1, 1),
                                    Notification.created_at < datetime(year + 1, 1, 1)
                                )
                        elif len(search) == 10 and search.count('-') == 2:  # Full date YYYY-MM-DD
                            # Validate date format
                            try:
                                search_date = datetime.strptime(search, '%Y-%m-%d')
                                query = query.filter(
                                    Notification.created_at >= search_date,
                                    Notification.created_at < search_date + timedelta(days=1)
                                )
                            except ValueError:
                                # Invalid date format - return no results
                                query = query.filter(Notification.id == -1)  # Impossible condition
                        else:
                            # Invalid format - return no results
                            query = query.filter(Notification.id == -1)  # Impossible condition
                    except (ValueError, TypeError):
                        # Fallback to no results if date parsing fails
                        query = query.filter(Notification.id == -1)  # Impossible condition
            
            # Get total count
            total_count = query.count()
            
            # Get paginated results
            notifications = query.order_by(
                Notification.created_at.desc()
            ).offset((page - 1) * per_page).limit(per_page).all()
            
            return notifications, total_count
        except Exception as e:
            current_app.logger.error(f"Error getting paginated user notifications: {str(e)}")
            return [], 0
    
    def get_user_notifications_all_paginated(self, user_id: int, page: int = 1, per_page: int = 20, search: Optional[str] = None, search_mode: str = 'message') -> tuple[List[Notification], int]:
        """Get all paginated notifications (both sent and pending) for a specific user.
        
        Args:
            user_id: The ID of the user to get notifications for
            page: Page number (1-based)
            per_page: Number of notifications per page
            search: Optional search term to filter notifications
            search_mode: Search mode ('message', 'item', 'email', 'date')
            
        Returns:
            Tuple of (notifications, total_count)
        """
        try:
            query = Notification.query.filter_by(
                user_id=user_id,
                type='email'
            )
            
            # Add search filter based on mode
            if search:
                if search_mode == 'message':
                    query = query.filter(Notification.message.ilike(f'%{search}%'))
                elif search_mode == 'date':
                    # Search by date in created_at only (not message content)
                    try:
                        if len(search) == 4 and search.isdigit():  # Year only
                            year = int(search)
                            if 1900 <= year <= 2100:
                                query = query.filter(
                                    Notification.created_at >= datetime(year, 1, 1),
                                    Notification.created_at < datetime(year + 1, 1, 1)
                                )
                        elif len(search) == 10 and search.count('-') == 2:  # Full date YYYY-MM-DD
                            # Validate date format
                            try:
                                search_date = datetime.strptime(search, '%Y-%m-%d')
                                query = query.filter(
                                    Notification.created_at >= search_date,
                                    Notification.created_at < search_date + timedelta(days=1)
                                )
                            except ValueError:
                                # Invalid date format - return no results
                                query = query.filter(Notification.id == -1)  # Impossible condition
                        else:
                            # Invalid format - return no results
                            query = query.filter(Notification.id == -1)  # Impossible condition
                    except (ValueError, TypeError):
                        # Fallback to no results if date parsing fails
                        query = query.filter(Notification.id == -1)  # Impossible condition
            
            # Get total count
            total_count = query.count()
            
            # Get paginated results
            notifications = query.order_by(
                Notification.created_at.desc()
            ).offset((page - 1) * per_page).limit(per_page).all()
            
            return notifications, total_count
        except Exception as e:
            current_app.logger.error(f"Error getting all paginated user notifications: {str(e)}")
            return [], 0 