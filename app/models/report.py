from datetime import datetime
from app.core.extensions import db
from app.models.base import BaseModel

class Report(BaseModel):
    """Model for storing daily inventory reports."""
    
    __tablename__ = 'reports'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    total_items = db.Column(db.Integer, default=0)
    total_value = db.Column(db.Float, default=0.0)
    expiring_items = db.Column(db.Integer, default=0)
    expired_items = db.Column(db.Integer, default=0)
    low_stock_items = db.Column(db.Integer, default=0)
    total_sales = db.Column(db.Float, default=0.0)
    total_purchases = db.Column(db.Float, default=0.0)
    report_data = db.Column(db.JSON)  # Store detailed report data
    is_public = db.Column(db.Boolean, default=False)  # Whether report is publicly accessible
    public_token = db.Column(db.String(64), unique=True)  # Token for public access
    
    # Add unique constraint on date and user_id together
    __table_args__ = (
        db.UniqueConstraint('date', 'user_id', name='unique_report_per_user_per_date'),
    )
    
    # Add relationship to User model
    user = db.relationship('User', backref=db.backref('reports', lazy=True))
    
    def __init__(self, **kwargs):
        """Initialize report with given parameters."""
        super().__init__()
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def to_dict(self):
        """Convert report to dictionary."""
        data = super().to_dict()
        data.update({
            'date': self.date.strftime('%Y-%m-%d'),
            'total_items': self.total_items,
            'total_value': self.total_value,
            'expiring_items': self.expiring_items,
            'expired_items': self.expired_items,
            'low_stock_items': self.low_stock_items,
            'total_sales': self.total_sales,
            'total_purchases': self.total_purchases,
            'report_data': self.report_data,
            'is_public': self.is_public,
            'public_token': self.public_token
        })
        return data
    
    def __repr__(self):
        """String representation of the report."""
        return f'<Report {self.date}>' 