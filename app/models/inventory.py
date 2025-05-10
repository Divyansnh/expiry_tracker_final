from datetime import datetime
from app import db

STATUS_PENDING = 'pending_expiry_date'
STATUS_ACTIVE = 'active'
STATUS_EXPIRING_SOON = 'expiring_soon'
STATUS_EXPIRED = 'expired'

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expiry_date = db.Column(db.Date)
    status = db.Column(db.String(20), default=STATUS_PENDING)
    
    def update_status(self):
        """Update the item's status based on its expiry date"""
        if not self.expiry_date:
            self.status = STATUS_PENDING
            return
        
        today = datetime.now().date()
        days_until_expiry = (self.expiry_date - today).days
        
        if days_until_expiry < 0:
            self.status = STATUS_EXPIRED
        elif days_until_expiry <= 7:
            self.status = STATUS_EXPIRING_SOON
        else:
            self.status = STATUS_ACTIVE 