from app.models.activity import Activity
from app.core.extensions import db
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

class ActivityService:
    """Service for managing user activities."""
    
    def __init__(self):
        pass
    
    def log_activity(self, user_id: int, activity_type: str, title: str, 
                    description: Optional[str] = None, activity_data: Optional[Dict[str, Any]] = None) -> Activity:
        """Log a new activity for a user."""
        try:
            activity = Activity(  # type: ignore
                user_id=user_id,
                activity_type=activity_type,
                title=title,
                description=description,
                activity_data=activity_data
            )
            
            db.session.add(activity)
            db.session.commit()
            
            return activity
        except Exception as e:
            db.session.rollback()
            raise e
    
    def get_user_activities(self, user_id: int, limit: int = 10, 
                          activity_types: Optional[List[str]] = None) -> List[Activity]:
        """Get recent activities for a user."""
        query = Activity.query.filter_by(user_id=user_id)
        
        if activity_types:
            query = query.filter(Activity.activity_type.in_(activity_types))
        
        return query.order_by(Activity.created_at.desc()).limit(limit).all()
    
    def get_activities_by_date_range(self, user_id: int, start_date: datetime, 
                                   end_date: datetime) -> List[Activity]:
        """Get activities within a date range."""
        return Activity.query.filter(
            Activity.user_id == user_id,
            Activity.created_at >= start_date,
            Activity.created_at <= end_date
        ).order_by(Activity.created_at.desc()).all()
    
    def get_recent_activities_for_dashboard(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent activities formatted for dashboard display."""
        activities = self.get_user_activities(user_id, limit=limit)
        
        formatted_activities = []
        for activity in activities:
            activity_dict = activity.to_dict()
            activity_dict['icon'] = Activity.get_activity_icon(activity.activity_type)
            activity_dict['color'] = Activity.get_activity_color(activity.activity_type)
            formatted_activities.append(activity_dict)
        
        return formatted_activities
    
    def get_activities_paginated(self, user_id: int, page: int = 1, per_page: int = 20,
                                activity_type: str = 'all') -> tuple[List[Dict], int]:
        """Get paginated activities with filtering."""
        query = Activity.query.filter_by(user_id=user_id)
        
        # Apply activity type filter
        if activity_type and activity_type != 'all':
            query = query.filter(Activity.activity_type == activity_type)
        
        # Get total count
        total_count = query.count()
        
        # Apply pagination
        activities = query.order_by(Activity.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
        
        # Format activities
        formatted_activities = []
        for activity in activities:
            activity_dict = activity.to_dict()
            activity_dict['icon'] = Activity.get_activity_icon(activity.activity_type)
            activity_dict['color'] = Activity.get_activity_color(activity.activity_type)
            formatted_activities.append(activity_dict)
        
        return formatted_activities, total_count
    
    def log_item_added(self, user_id: int, item_name: str, item_id: int) -> Activity:
        """Log when an item is added."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.ITEM_ADDED,
            title="New item added",
            description=f'Product "{item_name}" was added to inventory',
            activity_data={'item_id': item_id, 'item_name': item_name}
        )
    
    def log_item_updated(self, user_id: int, item_name: str, item_id: int, 
                        changes: Dict[str, Any]) -> Activity:
        """Log when an item is updated."""
        change_descriptions = []
        for field, value in changes.items():
            if field == 'quantity':
                change_descriptions.append(f"Quantity updated to {value}")
            elif field == 'expiry_date':
                change_descriptions.append(f"Expiry date updated to {value}")
            elif field == 'cost_price':
                change_descriptions.append(f"Cost price updated to £{value}")
            else:
                change_descriptions.append(f"{field.title()} updated")
        
        description = f'Updated "{item_name}": {", ".join(change_descriptions)}'
        
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.ITEM_UPDATED,
            title="Item updated",
            description=description,
            activity_data={'item_id': item_id, 'item_name': item_name, 'changes': changes}
        )
    
    def log_item_deleted(self, user_id: int, item_name: str, item_id: int) -> Activity:
        """Log when an item is deleted."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.ITEM_DELETED,
            title="Item deleted",
            description=f'Product "{item_name}" was removed from inventory',
            activity_data={'item_id': item_id, 'item_name': item_name}
        )
    
    def log_expiry_alert(self, user_id: int, item_name: str, days_until_expiry: int) -> Activity:
        """Log when an expiry alert is triggered."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.EXPIRY_ALERT,
            title="Expiry alert",
            description=f'"{item_name}" expires in {days_until_expiry} days',
            activity_data={'item_name': item_name, 'days_until_expiry': days_until_expiry}
        )
    
    def log_notification_sent(self, user_id: int, notification_type: str, 
                            item_count: int = 1) -> Activity:
        """Log when a notification is sent."""
        description = f"{notification_type} notification sent"
        if item_count > 1:
            description += f" for {item_count} items"
        
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.NOTIFICATION_SENT,
            title="Notification sent",
            description=description,
            activity_data={'notification_type': notification_type, 'item_count': item_count}
        )
    
    def log_report_generated(self, user_id: int, report_type: str) -> Activity:
        """Log when a report is generated."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.REPORT_GENERATED,
            title="Report generated",
            description=f"{report_type} report created",
            activity_data={'report_type': report_type}
        )
    
    def log_settings_updated(self, user_id: int, setting_name: str) -> Activity:
        """Log when settings are updated."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.SETTINGS_UPDATED,
            title="Settings updated",
            description=f"{setting_name} setting was modified",
            activity_data={'setting_name': setting_name}
        )
    
    def log_zoho_sync(self, user_id: int, sync_type: str, success: bool, 
                     item_count: int = 0) -> Activity:
        """Log Zoho sync activities."""
        status = "successful" if success else "failed"
        description = f"Zoho {sync_type} sync {status}"
        if item_count > 0:
            description += f" ({item_count} items)"
        
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.ZOHO_SYNC,
            title=f"Zoho {sync_type.title()} sync",
            description=description,
            activity_data={'sync_type': sync_type, 'success': success, 'item_count': item_count}
        )
    
    def log_login(self, user_id: int) -> Activity:
        """Log user login."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.LOGIN,
            title="User logged in",
            description="User successfully logged into the system"
        )
    
    def log_logout(self, user_id: int) -> Activity:
        """Log user logout."""
        return self.log_activity(
            user_id=user_id,
            activity_type=Activity.LOGOUT,
            title="User logged out",
            description="User logged out of the system"
        )
    
    def cleanup_old_activities(self, days_to_keep: int = 90) -> int:
        """Clean up activities older than specified days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
        
        deleted_count = Activity.query.filter(
            Activity.created_at < cutoff_date
        ).delete()
        
        db.session.commit()
        return deleted_count 