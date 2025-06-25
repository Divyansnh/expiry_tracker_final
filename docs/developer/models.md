# Models

This document provides a comprehensive overview of the data models in the Expiry Tracker application.

## Overview

The application uses SQLAlchemy ORM for data modeling and database interactions. All models inherit from a base model that provides common functionality like timestamps and ID management.

## Base Model

**Location:** `app/models/base.py`

**Purpose:** Provides common functionality for all models.

```python
from app.core.extensions import db
from datetime import datetime

class BaseModel(db.Model):
    """Base model class that includes common fields and methods."""
    
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def save(self):
        """Save the model to the database."""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """Delete the model from the database."""
        db.session.delete(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert model to dictionary representation."""
        return {
            'id': self.id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
```

## User Model

**Location:** `app/models/user.py`

**Purpose:** Represents user accounts and authentication information.

```python
from app.models.base import BaseModel
from app.core.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import os

class User(BaseModel, UserMixin):
    """User model for authentication and account management."""
    
    __tablename__ = 'users'
    
    # Authentication fields
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Email verification
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255))
    reset_password_token = db.Column(db.String(255))
    reset_password_expires = db.Column(db.DateTime)
    
    # Zoho integration
    zoho_access_token = db.Column(db.Text)
    zoho_refresh_token = db.Column(db.Text)
    zoho_organization_id = db.Column(db.String(255))
    zoho_organization_name = db.Column(db.String(255))
    zoho_credentials_encrypted = db.Column(db.Text)
    zoho_credentials_salt = db.Column(db.String(255))
    zoho_credentials_iv = db.Column(db.String(255))
    zoho_disconnect_email_code = db.Column(db.String(255))
    zoho_disconnect_email_code_expires = db.Column(db.DateTime)
    
    # Preferences
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Relationships
    items = db.relationship('Item', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert user to dictionary (excluding sensitive data)."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'email_verified': self.email_verified,
            'zoho_organization_name': self.zoho_organization_name,
            'email_notifications': self.email_notifications,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_id(self):
        """Return user ID for Flask-Login."""
        return str(self.id)
```

## Item Model

**Location:** `app/models/item.py`

**Purpose:** Represents inventory items with expiry tracking.

```python
from app.models.base import BaseModel
from app.core.extensions import db
from datetime import datetime, date, timedelta

class Item(BaseModel):
    """Item model for inventory management."""
    
    __tablename__ = 'items'
    
    # Basic information
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Quantity and pricing
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    unit = db.Column(db.String(20), nullable=False)
    selling_price = db.Column(db.Numeric(10, 2))
    cost_price = db.Column(db.Numeric(10, 2))
    
    # Expiry tracking
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    
    # Zoho integration
    zoho_item_id = db.Column(db.String(255))
    
    # Status constants
    STATUS_ACTIVE = 'active'
    STATUS_EXPIRED = 'expired'
    STATUS_EXPIRING_SOON = 'expiring_soon'
    STATUS_PENDING = 'pending'
    
    def __repr__(self):
        return f'<Item {self.name}>'
    
    def update_status(self, force_update=False):
        """Update item status based on expiry date."""
        if not self.expiry_date:
            self.status = self.STATUS_PENDING
            return
        
        today = date.today()
        days_until_expiry = (self.expiry_date - today).days
        
        if days_until_expiry < 0:
            self.status = self.STATUS_EXPIRED
        elif days_until_expiry <= 30:
            self.status = self.STATUS_EXPIRING_SOON
        else:
            self.status = self.STATUS_ACTIVE
    
    def get_days_until_expiry(self):
        """Get days until expiry (negative if expired)."""
        if not self.expiry_date:
            return None
        return (self.expiry_date - date.today()).days
    
    def get_total_value(self):
        """Calculate total value based on quantity and cost price."""
        if self.quantity and self.cost_price:
            return float(self.quantity * self.cost_price)
        return 0.0
    
    def to_dict(self):
        """Convert item to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'description': self.description,
            'quantity': float(self.quantity) if self.quantity else 0,
            'unit': self.unit,
            'selling_price': float(self.selling_price) if self.selling_price else None,
            'cost_price': float(self.cost_price) if self.cost_price else None,
            'expiry_date': self.expiry_date.isoformat() if self.expiry_date else None,
            'status': self.status,
            'zoho_item_id': self.zoho_item_id,
            'days_until_expiry': self.get_days_until_expiry(),
            'total_value': self.get_total_value(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_expiring_items(cls, user_id, days=30):
        """Get items expiring within specified days."""
        future_date = date.today() + timedelta(days=days)
        return cls.query.filter(
            cls.user_id == user_id,
            cls.expiry_date <= future_date,
            cls.expiry_date >= date.today()
        ).all()
    
    @classmethod
    def get_expired_items(cls, user_id):
        """Get expired items."""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.expiry_date < date.today()
        ).all()
```

## Activity Model

**Location:** `app/models/activity.py`

**Purpose:** Tracks user activities and system events for audit trail.

```python
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
            return f"{diff.days} days ago"
        elif diff.seconds > 3600:
            hours = diff.seconds // 3600
            return f"{hours} hours ago"
        elif diff.seconds > 60:
            minutes = diff.seconds // 60
            return f"{minutes} minutes ago"
        else:
            return "Just now"
    
    @staticmethod
    def get_activity_icon(activity_type):
        """Get FontAwesome icon for activity type."""
        icons = {
            Activity.ITEM_ADDED: "fas fa-plus",
            Activity.ITEM_UPDATED: "fas fa-edit",
            Activity.ITEM_DELETED: "fas fa-trash",
            Activity.EXPIRY_ALERT: "fas fa-exclamation-triangle",
            Activity.NOTIFICATION_SENT: "fas fa-envelope",
            Activity.REPORT_GENERATED: "fas fa-chart-bar",
            Activity.SETTINGS_UPDATED: "fas fa-cog",
            Activity.ZOHO_SYNC: "fas fa-sync",
            Activity.LOGIN: "fas fa-sign-in-alt",
            Activity.LOGOUT: "fas fa-sign-out-alt"
        }
        return icons.get(activity_type, "fas fa-info-circle")
    
    @staticmethod
    def get_activity_color(activity_type):
        """Get color class for activity type."""
        colors = {
            Activity.ITEM_ADDED: "green",
            Activity.ITEM_UPDATED: "blue",
            Activity.ITEM_DELETED: "red",
            Activity.EXPIRY_ALERT: "yellow",
            Activity.NOTIFICATION_SENT: "blue",
            Activity.REPORT_GENERATED: "purple",
            Activity.SETTINGS_UPDATED: "gray",
            Activity.ZOHO_SYNC: "indigo",
            Activity.LOGIN: "green",
            Activity.LOGOUT: "gray"
        }
        return colors.get(activity_type, "gray")
```

## Notification Model

**Location:** `app/models/notification.py`

**Purpose:** Represents email notifications and their delivery status.

```python
from app.models.base import BaseModel
from app.core.extensions import db

class Notification(BaseModel):
    """Model for email notifications."""
    
    __tablename__ = 'notifications'
    
    # Fields
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'), ondelete='SET NULL')
    message = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(20), default='email')
    status = db.Column(db.String(20), default='pending')
    priority = db.Column(db.String(20), default='normal')
    sent_at = db.Column(db.DateTime)
    
    # Status constants
    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'
    
    # Type constants
    TYPE_EMAIL = 'email'
    TYPE_SMS = 'sms'
    TYPE_PUSH = 'push'
    
    # Priority constants
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    
    # Relationships
    item = db.relationship('Item', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'
    
    def to_dict(self):
        """Convert notification to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'item_id': self.item_id,
            'message': self.message,
            'type': self.type,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None
        }
    
    def mark_as_sent(self):
        """Mark notification as sent."""
        from datetime import datetime
        self.status = self.STATUS_SENT
        self.sent_at = datetime.utcnow()
        self.save()
    
    def mark_as_failed(self):
        """Mark notification as failed."""
        self.status = self.STATUS_FAILED
        self.save()
    
    @classmethod
    def get_pending_notifications(cls, user_id=None):
        """Get pending notifications."""
        query = cls.query.filter(cls.status == cls.STATUS_PENDING)
        if user_id:
            query = query.filter(cls.user_id == user_id)
        return query.all()
    
    @classmethod
    def get_user_notifications(cls, user_id, limit=20):
        """Get recent notifications for a user."""
        return cls.query.filter(cls.user_id == user_id)\
                       .order_by(cls.created_at.desc())\
                       .limit(limit)\
                       .all()
```

## Report Model

**Location:** `app/models/report.py`

**Purpose:** Represents generated inventory reports with historical data.

```python
from app.models.base import BaseModel
from app.core.extensions import db
from datetime import date

class Report(BaseModel):
    """Model for inventory reports."""
    
    __tablename__ = 'reports'
    
    # Fields
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    report_date = db.Column(db.Date, nullable=False)
    
    # Item counts
    total_items = db.Column(db.Integer, nullable=False, default=0)
    active_items = db.Column(db.Integer, nullable=False, default=0)
    expiring_items = db.Column(db.Integer, nullable=False, default=0)
    expired_items = db.Column(db.Integer, nullable=False, default=0)
    
    # Values
    total_value = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    active_value = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    expiring_value = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    expired_value = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    
    # Additional data
    report_data = db.Column(db.JSON, nullable=True)  # Store detailed report information
    
    def __repr__(self):
        return f'<Report {self.report_date} for User {self.user_id}>'
    
    def to_dict(self):
        """Convert report to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'report_date': self.report_date.isoformat() if self.report_date else None,
            'total_items': self.total_items,
            'active_items': self.active_items,
            'expiring_items': self.expiring_items,
            'expired_items': self.expired_items,
            'total_value': float(self.total_value) if self.total_value else 0,
            'active_value': float(self.active_value) if self.active_value else 0,
            'expiring_value': float(self.expiring_value) if self.expiring_value else 0,
            'expired_value': float(self.expired_value) if self.expired_value else 0,
            'report_data': self.report_data,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    @classmethod
    def get_user_reports(cls, user_id, limit=20):
        """Get recent reports for a user."""
        return cls.query.filter(cls.user_id == user_id)\
                       .order_by(cls.report_date.desc())\
                       .limit(limit)\
                       .all()
    
    @classmethod
    def get_report_by_date(cls, user_id, report_date):
        """Get report for specific date."""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.report_date == report_date
        ).first()
    
    @classmethod
    def get_historical_reports(cls, user_id, days=7):
        """Get reports from the last N days."""
        from datetime import timedelta
        start_date = date.today() - timedelta(days=days)
        return cls.query.filter(
            cls.user_id == user_id,
            cls.report_date >= start_date
        ).order_by(cls.report_date.desc()).all()
```

## Model Relationships

### One-to-Many Relationships

```python
# User has many Items
user.items = db.relationship('Item', backref='user', lazy='dynamic', cascade='all, delete-orphan')

# User has many Activities
user.activities = db.relationship('Activity', backref='user', lazy='dynamic', cascade='all, delete-orphan')

# User has many Notifications
user.notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

# User has many Reports
user.reports = db.relationship('Report', backref='user', lazy='dynamic', cascade='all, delete-orphan')

# Item has many Notifications
item.notifications = db.relationship('Notification', backref='item')
```

### Foreign Key Constraints

```python
# Items table
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# Activities table
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

# Notifications table
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
item_id = db.Column(db.Integer, db.ForeignKey('items.id'), ondelete='SET NULL')

# Reports table
user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
```

## Model Validation

### Field Validation

```python
from sqlalchemy.orm import validates

class Item(BaseModel):
    @validates('name')
    def validate_name(self, key, name):
        if not name or len(name.strip()) == 0:
            raise ValueError('Item name cannot be empty')
        if len(name) > 100:
            raise ValueError('Item name cannot exceed 100 characters')
        return name.strip()
    
    @validates('quantity')
    def validate_quantity(self, key, quantity):
        if quantity is not None and quantity < 0:
            raise ValueError('Quantity cannot be negative')
        return quantity
    
    @validates('selling_price', 'cost_price')
    def validate_prices(self, key, price):
        if price is not None and price < 0:
            raise ValueError('Price cannot be negative')
        return price
```

### Business Logic Validation

```python
class User(BaseModel):
    @validates('email')
    def validate_email(self, key, email):
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError('Invalid email format')
        return email.lower()
    
    @validates('username')
    def validate_username(self, key, username):
        if not username or len(username.strip()) == 0:
            raise ValueError('Username cannot be empty')
        if len(username) < 3 or len(username) > 20:
            raise ValueError('Username must be between 3 and 20 characters')
        if not username.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username can only contain letters, numbers, underscores, and hyphens')
        return username.lower()
```

## Model Methods

### Query Methods

```python
class Item(BaseModel):
    @classmethod
    def get_by_user(cls, user_id, status=None):
        """Get items for a user with optional status filter."""
        query = cls.query.filter(cls.user_id == user_id)
        if status:
            query = query.filter(cls.status == status)
        return query.all()
    
    @classmethod
    def search_by_name(cls, user_id, search_term):
        """Search items by name for a user."""
        return cls.query.filter(
            cls.user_id == user_id,
            cls.name.ilike(f'%{search_term}%')
        ).all()
    
    @classmethod
    def get_expiring_soon(cls, user_id, days=30):
        """Get items expiring within specified days."""
        from datetime import timedelta
        future_date = date.today() + timedelta(days=days)
        return cls.query.filter(
            cls.user_id == user_id,
            cls.expiry_date <= future_date,
            cls.expiry_date >= date.today()
        ).all()
```

### Instance Methods

```python
class Item(BaseModel):
    def is_expired(self):
        """Check if item is expired."""
        if not self.expiry_date:
            return False
        return self.expiry_date < date.today()
    
    def is_expiring_soon(self, days=30):
        """Check if item is expiring soon."""
        if not self.expiry_date:
            return False
        future_date = date.today() + timedelta(days=days)
        return self.expiry_date <= future_date and self.expiry_date >= date.today()
    
    def get_status_color(self):
        """Get CSS color class for status."""
        colors = {
            self.STATUS_ACTIVE: 'green',
            self.STATUS_EXPIRING_SOON: 'yellow',
            self.STATUS_EXPIRED: 'red',
            self.STATUS_PENDING: 'gray'
        }
        return colors.get(self.status, 'gray')
```

## Database Indexes

### Performance Indexes

```python
# User model indexes
__table_args__ = (
    db.Index('idx_users_email', 'email'),
    db.Index('idx_users_username', 'username'),
    db.Index('idx_users_email_verified', 'email_verified'),
)

# Item model indexes
__table_args__ = (
    db.Index('idx_items_user_id', 'user_id'),
    db.Index('idx_items_status', 'status'),
    db.Index('idx_items_expiry_date', 'expiry_date'),
    db.Index('idx_items_name_user', 'name', 'user_id'),
    db.Index('idx_items_zoho_id', 'zoho_item_id'),
)

# Activity model indexes
__table_args__ = (
    db.Index('idx_activities_user_id', 'user_id'),
    db.Index('idx_activities_type', 'activity_type'),
    db.Index('idx_activities_created_at', 'created_at'),
    db.Index('idx_activities_user_type', 'user_id', 'activity_type'),
)

# Notification model indexes
__table_args__ = (
    db.Index('idx_notifications_user_id', 'user_id'),
    db.Index('idx_notifications_status', 'status'),
    db.Index('idx_notifications_created_at', 'created_at'),
    db.Index('idx_notifications_item_id', 'item_id'),
)

# Report model indexes
__table_args__ = (
    db.Index('idx_reports_user_id', 'user_id'),
    db.Index('idx_reports_date', 'report_date'),
    db.Index('idx_reports_user_date', 'user_id', 'report_date'),
)
```

---

**Previous**: [Services Layer](./services.md) | **Next**: [Security Implementation](./security.md) 