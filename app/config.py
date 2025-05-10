import os
from datetime import timedelta
from typing import Optional

class Config:
    """Base configuration."""
    # Flask config
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'app/flask_session'
    SESSION_COOKIE_NAME = 'expiry_tracker_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # Set to True in production
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_DOMAIN = None
    SESSION_COOKIE_PATH = '/'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_REFRESH_EACH_REQUEST = True

    # Database config
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 5,
        'pool_recycle': 3600,
        'pool_pre_ping': True
    }

    # Email config
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')

    # Security config
    MAX_LOGIN_ATTEMPTS = 5
    LOGIN_LOCKOUT_TIME = timedelta(minutes=15)
    PASSWORD_RESET_EXPIRY = timedelta(hours=1)
    EMAIL_VERIFICATION_EXPIRY = timedelta(hours=24)

    # CORS config
    CORS_ORIGINS = ['http://localhost:5000', 'http://127.0.0.1:5000']
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_ALLOW_HEADERS = ['Content-Type', 'X-CSRFToken']
    CORS_EXPOSE_HEADERS = ['Content-Type', 'X-CSRFToken']

    # File upload config
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
    UPLOAD_FOLDER = 'app/static/uploads'

    # Logging config
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = 'app.log'

    # Cache config
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300

    # Rate limiting
    RATELIMIT_DEFAULT = "200 per day;50 per hour"
    RATELIMIT_STORAGE_URL = "memory://"

    # Zoho config
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET')
    ZOHO_REDIRECT_URI = os.environ.get('ZOHO_REDIRECT_URI')
    ZOHO_ACCESS_TOKEN_URL = "https://accounts.zoho.com/oauth/v2/token"
    ZOHO_AUTHORIZE_URL = "https://accounts.zoho.com/oauth/v2/auth"
    ZOHO_API_BASE_URL = "https://www.zohoapis.com/inventory/v1"

    # Twilio config
    TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
    TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
    TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

    # Notification config
    NOTIFICATION_EXPIRY_DAYS = 7
    NOTIFICATION_CHECK_INTERVAL = 3600  # 1 hour in seconds

    # Report config
    REPORT_EXPIRY_DAYS = 30
    REPORT_CLEANUP_INTERVAL = 86400  # 24 hours in seconds

    # API config
    API_PREFIX = '/api/v1'
    API_VERSION = '1.0'
    API_TITLE = 'Expiry Tracker API'
    API_DESCRIPTION = 'API for managing inventory and tracking expiry dates'
    API_TERMS_OF_SERVICE = 'http://example.com/terms/'
    API_CONTACT_EMAIL = 'support@example.com'
    API_LICENSE_NAME = 'MIT'
    API_LICENSE_URL = 'http://opensource.org/licenses/MIT'

    # Development specific config
    DEBUG = True
    TESTING = False
    TEMPLATES_AUTO_RELOAD = True
    EXPLAIN_TEMPLATE_LOADING = False
    PROPAGATE_EXCEPTIONS = True
    PRESERVE_CONTEXT_ON_EXCEPTION = True
    TRAP_HTTP_EXCEPTIONS = False
    TRAP_BAD_REQUEST_ERRORS = False
    JSON_AS_ASCII = False
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    JSONIFY_MIMETYPE = 'application/json'
    SEND_FILE_MAX_AGE_DEFAULT = 0
    MAX_COOKIE_SIZE = 4093

    # Production specific config
    PREFERRED_URL_SCHEME = 'https'
    SERVER_NAME = None
    APPLICATION_ROOT = '/'
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 year
    MAX_COOKIE_SIZE = 4093

    # Testing specific config
    TESTING = True
    WTF_CSRF_ENABLED = False
    PRESERVE_CONTEXT_ON_EXCEPTION = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SERVER_NAME = 'localhost'
    APPLICATION_ROOT = '/'
    PREFERRED_URL_SCHEME = 'http'
    MAX_COOKIE_SIZE = 4093

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    
    # Override required variables with development defaults
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')  # Only in development
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://localhost/expiry_tracker_v2')
    
    # Development session settings
    SESSION_TYPE = 'filesystem'
    SESSION_FILE_DIR = 'app/flask_session'
    SESSION_COOKIE_SECURE = False  # Allow non-HTTPS in development
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_NAME = 'expiry_tracker_session'
    SESSION_COOKIE_DOMAIN = None  # Allow all domains in development
    SESSION_COOKIE_PATH = '/'
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)  # 24 hours
    SESSION_REFRESH_EACH_REQUEST = True
    
    # CORS settings for development
    CORS_SUPPORTS_CREDENTIALS = True
    CORS_EXPOSE_HEADERS = ['Set-Cookie']
    CORS_ALLOW_HEADERS = ['Content-Type', 'Authorization', 'X-CSRFToken']
    CORS_METHODS = ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS']
    
    # Development Zoho settings
    ZOHO_CLIENT_ID = os.environ.get('ZOHO_CLIENT_ID', 'dev-client-id')
    ZOHO_CLIENT_SECRET = os.environ.get('ZOHO_CLIENT_SECRET', 'dev-client-secret')
    ZOHO_REDIRECT_URI = os.environ.get('ZOHO_REDIRECT_URI', 'http://localhost:5000/auth/zoho/callback')
    ZOHO_ORGANIZATION_ID = os.environ.get('ZOHO_ORGANIZATION_ID', 'dev-org-id')

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False
    
    # Production session settings
    SESSION_COOKIE_SECURE = True  # Require HTTPS in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'  # More restrictive in production
    
    # Production-specific database settings
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10
    }
    
    # Production Zoho settings
    ZOHO_CLIENT_ID = os.environ['ZOHO_CLIENT_ID']  # Required in production
    ZOHO_CLIENT_SECRET = os.environ['ZOHO_CLIENT_SECRET']  # Required in production
    ZOHO_REDIRECT_URI = os.environ['ZOHO_REDIRECT_URI']  # Required in production
    ZOHO_ORGANIZATION_ID = os.environ.get('ZOHO_ORGANIZATION_ID', '')

class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    
    # Use in-memory SQLite for testing
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Testing-specific settings
    SECRET_KEY = 'test-secret-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # Disable CSRF protection in testing
    WTF_CSRF_ENABLED = False
    
    # Testing Zoho settings
    ZOHO_CLIENT_ID = 'test-client-id'
    ZOHO_CLIENT_SECRET = 'test-client-secret'
    ZOHO_REDIRECT_URI = 'http://localhost:5000/auth/zoho/callback'
    ZOHO_ORGANIZATION_ID = 'test-org-id'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 