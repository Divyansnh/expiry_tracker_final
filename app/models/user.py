from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app.core.extensions import db
from app.models.base import BaseModel
from datetime import datetime, timedelta
import jwt
from flask import current_app
from time import time
import secrets
import string
import re
import bcrypt
from typing import Optional

class User(UserMixin, BaseModel):
    """User model for authentication and user management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    notification_preferences = db.Column(db.JSON, default=dict)
    
    # Security fields
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    # Verification fields
    verification_code = db.Column(db.String(32))
    verification_code_expires_at = db.Column(db.DateTime)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Notification preferences
    email_notifications = db.Column(db.Boolean, default=True)
    
    # Relationships
    items = db.relationship('Item', back_populates='user', lazy='dynamic')
    notifications = db.relationship('Notification', back_populates='user', lazy='dynamic')
    
    # Zoho integration fields
    zoho_client_id = db.Column(db.String(255))
    zoho_client_secret = db.Column(db.String(255))
    zoho_access_token = db.Column(db.String(255))
    zoho_refresh_token = db.Column(db.String(255))
    zoho_token_expires_at = db.Column(db.DateTime)
    zoho_organization_id = db.Column(db.String(255))
    
    # Password reset fields
    password_reset_token = db.Column(db.String(256))
    password_reset_token_expires_at = db.Column(db.DateTime)
    
    def __init__(self, username=None, email=None, is_verified=False):
        self.username = username
        self.email = email
        self.is_verified = is_verified
        # Set default notification preferences
        self.email_notifications = True  # Enable email notifications by default
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        if not self._is_strong_password(password):
            raise ValueError(
                "Password must be at least 8 characters long and contain:\n"
                "- At least one uppercase letter\n"
                "- At least one lowercase letter\n"
                "- At least one number\n"
                "- At least one special character"
            )
        # Generate a new salt for each password
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verify_password(self, password: str) -> bool:
        """Verify a password against the stored hash."""
        if not self.password_hash:
            return False
            
        # Verify password using bcrypt
        try:
            is_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                self.password_hash.encode('utf-8')
            )
        except ValueError:
            # Handle potential invalid hash format
            return False
        
        if is_valid:
            self.last_login = datetime.utcnow()
            db.session.commit()
            
        return is_valid
    
    def is_locked(self) -> bool:
        """Check if the account is currently locked."""
        if not self.locked_until:
            return False
        # If lockout has expired, clear the lock
        if datetime.utcnow() > self.locked_until:
            self.locked_until = None
            self.login_attempts = 0
            db.session.commit()
            return False
        return True
    
    def get_lockout_time_remaining(self) -> Optional[timedelta]:
        """Get the remaining lockout time if account is locked."""
        if not self.locked_until:
            return None
        now = datetime.utcnow()
        if now > self.locked_until:
            self.locked_until = None
            self.login_attempts = 0
            db.session.commit()
            return None
        return self.locked_until - now
    
    def _is_strong_password(self, password: str) -> bool:
        """Check if password meets strength requirements."""
        if len(password) < 8:
            return False
        
        # Check for at least one uppercase letter
        if not re.search(r'[A-Z]', password):
            return False
        
        # Check for at least one lowercase letter
        if not re.search(r'[a-z]', password):
            return False
        
        # Check for at least one number
        if not re.search(r'[0-9]', password):
            return False
        
        # Check for at least one special character
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False
            
        return True
    
    def generate_verification_code(self):
        """Generate email verification code."""
        # Generate a 6-digit verification code
        self.verification_code = ''.join(secrets.choice(string.digits) for _ in range(6))
        self.verification_code_expires_at = datetime.utcnow() + timedelta(hours=1)
        self.save()
        return self.verification_code
    
    def verify_code(self, code):
        """Verify email verification code."""
        if (self.verification_code != code or 
            not self.verification_code_expires_at or 
            self.verification_code_expires_at < datetime.utcnow()):
            return False
        self.is_verified = True
        self.verification_code = None
        self.verification_code_expires_at = None
        db.session.add(self)
        db.session.commit()
        return True
    
    def save(self):
        """Save user to database."""
        db.session.add(self)
        db.session.commit()
    
    def to_dict(self):
        """Convert user to dictionary."""
        data = super().to_dict()
        data.update({
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'is_verified': self.is_verified,
            'email_notifications': self.email_notifications
        })
        return data
    
    def __repr__(self):
        """String representation of the user."""
        return f'<User {self.username}>'

    def generate_password_reset_token(self, expires_in: int = 3600) -> str:
        """Generate a password reset token using JWT."""
        try:
            payload = {
                'reset_password': self.id,
                'email': self.email,
                'exp': time() + expires_in
            }
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            self.password_reset_token = token
            self.password_reset_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
            db.session.commit()
            return token
        except Exception as e:
            current_app.logger.error(f"Error generating password reset token: {str(e)}")
            raise
    
    def verify_password_reset_token(self, token: str) -> bool:
        """Verify a password reset token."""
        try:
            if not token or not self.password_reset_token:
                return False
                
            # First verify the JWT token
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256']
            )
            
            # Check if token matches what's stored in database
            if not secrets.compare_digest(self.password_reset_token, token):
                return False
                
            # Check if token has expired
            if not self.password_reset_token_expires_at:
                return False
            if datetime.utcnow() > self.password_reset_token_expires_at:
                return False
                
            # Verify the user ID and email match
            if payload.get('reset_password') != self.id or payload.get('email') != self.email:
                return False
                
            return True
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Password reset token has expired")
            return False
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Invalid password reset token: {str(e)}")
            return False
        except Exception as e:
            current_app.logger.error(f"Error verifying password reset token: {str(e)}")
            return False
    
    def clear_password_reset_token(self):
        """Clear the password reset token."""
        self.password_reset_token = None
        self.password_reset_token_expires_at = None
        db.session.commit()

    @staticmethod
    def verify_reset_token(token: str) -> Optional['User']:
        """Static method to verify a password reset token and return the user."""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'],
                               algorithms=['HS256'])
            user_id = payload['reset_password']
            email = payload.get('email')
            used = payload.get('used', False)
            exp = payload.get('exp')
            
            current_app.logger.info(f"Verifying password reset token for user {user_id}")
            current_app.logger.debug(f"Token payload: {payload}")
            
            # Check if token has expired
            if exp and time() > exp:
                current_app.logger.warning(f"Token has expired for user {user_id}")
                return None
                
            # Check if token has already been used
            if used:
                current_app.logger.warning(f"Token has already been used for user {user_id}")
                return None
                
            user = User.query.get(user_id)
            if not user:
                current_app.logger.warning(f"User {user_id} not found")
                return None
                
            # Verify that the email matches
            if user.email != email:
                current_app.logger.warning(f"Email mismatch for user {user_id}. Token email: {email}, User email: {user.email}")
                return None
                
            # Verify that the token matches what's stored in the database
            if user.password_reset_token != token:
                current_app.logger.warning(f"Token mismatch for user {user_id}")
                return None
                
            return user
        except jwt.ExpiredSignatureError:
            current_app.logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError as e:
            current_app.logger.warning(f"Invalid token: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Error verifying token: {str(e)}")
            return None 