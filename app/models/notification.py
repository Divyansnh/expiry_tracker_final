from datetime import datetime
from app.core.extensions import db
from app.models.base import BaseModel

class Notification(BaseModel):
    """Model for storing user notifications."""
    
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # 'email', 'in_app'
    priority = db.Column(db.String(10), nullable=False)  # 'normal', 'high'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # 'pending', 'sent'
    
    # Add check constraint for priority and type
    __table_args__ = (
        db.CheckConstraint(
            "priority IN ('normal', 'high')",
            name='check_notification_priority'
        ),
        db.CheckConstraint(
            "type IN ('email', 'in_app')",
            name='check_notification_type'
        ),
        db.CheckConstraint(
            "status IN ('pending', 'sent')",
            name='check_notification_status'
        ),
    )
    
    # Relationships
    user = db.relationship('User', back_populates='notifications')
    item = db.relationship('Item', back_populates='notifications')
    
    def to_dict(self) -> dict:
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'message': self.message,
            'type': self.type,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Notification {self.id}: {self.message}>'
    
    def mark_as_read(self):
        """Mark the notification as read."""
        self.status = 'sent'
        db.session.commit() 