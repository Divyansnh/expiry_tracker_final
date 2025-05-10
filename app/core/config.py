import os
from dotenv import load_dotenv
import datetime

# Force reload of environment variables
load_dotenv(override=True)

class Config:
    """Base configuration."""
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-please-change-in-production'
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:postgres@localhost:5432/inventory_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,  # Recycle connections after 1 hour
        'pool_pre_ping': True,  # Enable connection health checks
        'pool_timeout': 30,     # Connection timeout in seconds
        'max_overflow': 20      # Maximum number of connections that can be created beyond pool_size
    }
    
    # File Upload
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = 16777216  # 16MB in bytes
    
    # Zoho Integration
    ZOHO_API_BASE_URL = 'https://www.zohoapis.eu/inventory/v1'
    ZOHO_ACCOUNTS_URL = 'https://accounts.zoho.eu'
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET')
    ZOHO_REDIRECT_URI = os.environ.get('ZOHO_REDIRECT_URI') or 'http://localhost:5000/auth/zoho/callback'
    
    # Twilio Integration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
    
    # Email Configuration
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    
    # Notification Settings
    try:
        NOTIFICATION_DAYS = [int(d.strip()) for d in os.getenv('NOTIFICATION_DAYS', '30,15,7,3,1').split(',')]
    except (ValueError, AttributeError):
        NOTIFICATION_DAYS = [30, 15, 7, 3, 1]
    
    # Session configuration
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'flask_session')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'session'
    SESSION_COOKIE_MAX_AGE = 24 * 60 * 60  # 24 hours
    SESSION_COOKIE_EXPIRES = datetime.timedelta(hours=24) 