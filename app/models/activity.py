from app.models.base import BaseModel
from app.core.extensions import db
from datetime import datetime

class Activity(BaseModel):
    """Model for tracking user activities."""
    
    __tablename__ = 'activities'
    
    # Activity types
    ITEM_ADDED = 'item_added'
    ITEM_UPDATED = 'item_updated'
    ITEM_DELETED = 'item_deleted'
    EXPIRY_ALERT = 'expiry_alert'
    NOTIFICATION_SENT = 'notification_sent'
    REPORT_GENERATED = 'report_generated'
    SETTINGS_UPDATED = 'settings_updated'
    ZOHO_SYNC = 'zoho_sync'
    LOGIN = 'login'
    LOGOUT = 'logout'
    
    # Fields
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    activity_data = db.Column(db.JSON, nullable=True)  # Store additional data like item_id, old_values, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='activities')
    
    def __repr__(self):
        return f'<Activity {self.activity_type} by User {self.user_id}>'
    
    def to_dict(self):
        """Convert activity to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'activity_type': self.activity_type,
            'title': self.title,
            'description': self.description,
            'activity_data': self.activity_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'time_ago': self.get_time_ago()
        }
    
    def get_time_ago(self):
        """Get human-readable time ago string."""
        if not self.created_at:
            return "Unknown"
        
        now = datetime.utcnow()
        diff = now - self.created_at
        
        if diff.days > 0:
            if diff.days == 1:
                return "1 day ago"
            return f"{diff.days} days ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            if hours == 1:
                return "1 hour ago"
            return f"{hours} hours ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            if minutes == 1:
                return "1 minute ago"
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    
    @classmethod
    def get_activity_icon(cls, activity_type):
        """Get FontAwesome icon for activity type."""
        icons = {
            cls.ITEM_ADDED: 'fas fa-plus',
            cls.ITEM_UPDATED: 'fas fa-edit',
            cls.ITEM_DELETED: 'fas fa-trash',
            cls.EXPIRY_ALERT: 'fas fa-exclamation-triangle',
            cls.NOTIFICATION_SENT: 'fas fa-bell',
            cls.REPORT_GENERATED: 'fas fa-chart-bar',
            cls.SETTINGS_UPDATED: 'fas fa-cog',
            cls.ZOHO_SYNC: 'fas fa-sync',
            cls.LOGIN: 'fas fa-sign-in-alt',
            cls.LOGOUT: 'fas fa-sign-out-alt'
        }
        return icons.get(activity_type, 'fas fa-info-circle')
    
    @classmethod
    def get_activity_color(cls, activity_type):
        """Get color class for activity type."""
        colors = {
            cls.ITEM_ADDED: 'green',
            cls.ITEM_UPDATED: 'blue',
            cls.ITEM_DELETED: 'red',
            cls.EXPIRY_ALERT: 'yellow',
            cls.NOTIFICATION_SENT: 'purple',
            cls.REPORT_GENERATED: 'gray',
            cls.SETTINGS_UPDATED: 'indigo',
            cls.ZOHO_SYNC: 'cyan',
            cls.LOGIN: 'green',
            cls.LOGOUT: 'gray'
        }
        return colors.get(activity_type, 'gray') 