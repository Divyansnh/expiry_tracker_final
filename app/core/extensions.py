from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_mail import Mail
from flask_session import Session
from flask_wtf.csrf import CSRFProtect
import os
from datetime import timedelta
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from typing import cast, Any

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
scheduler = APScheduler()
cors = CORS()
jwt = JWTManager()
mail = Mail()
csrf = CSRFProtect()

def init_extensions(app):
    """Initialize Flask extensions."""
    # Configure session first
    if 'SESSION_TYPE' not in app.config:
        app.config['SESSION_TYPE'] = 'filesystem'
    if 'SESSION_FILE_DIR' not in app.config:
        app.config['SESSION_FILE_DIR'] = os.path.join(app.root_path, 'flask_session')
    if 'SESSION_FILE_THRESHOLD' not in app.config:
        app.config['SESSION_FILE_THRESHOLD'] = 100
    if 'PERMANENT_SESSION_LIFETIME' not in app.config:
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)
    if 'SESSION_COOKIE_NAME' not in app.config:
        app.config['SESSION_COOKIE_NAME'] = 'expiry_tracker_session'
    if 'SESSION_COOKIE_MAX_AGE' not in app.config:
        app.config['SESSION_COOKIE_MAX_AGE'] = 24 * 60 * 60  # 24 hours in seconds
    if 'SESSION_COOKIE_EXPIRES' not in app.config:
        app.config['SESSION_COOKIE_EXPIRES'] = timedelta(hours=24)
    
    # Initialize session
    Session(app)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize login manager
    login_manager.init_app(app)
    # Use cast to handle type checking for login_view
    cast(Any, login_manager).login_view = 'auth.login'
    login_manager.login_message_category = 'info'
    
    # Initialize JWT manager
    jwt.init_app(app)
    
    # Initialize migrations
    migrate.init_app(app, db)
    
    # Initialize CORS with proper configuration
    cors.init_app(app, supports_credentials=True, resources={
        r"/*": {
            "origins": ["http://localhost:5000", "http://127.0.0.1:5000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "X-CSRFToken"],
            "supports_credentials": True
        }
    })
    
    # Initialize mail
    mail.init_app(app)
    
    # Log mail server configuration
    print("Mail server configuration:")
    print(f"MAIL_SERVER: {app.config.get('MAIL_SERVER')}")
    print(f"MAIL_PORT: {app.config.get('MAIL_PORT')}")
    print(f"MAIL_USE_TLS: {app.config.get('MAIL_USE_TLS')}")
    print(f"MAIL_USERNAME: {app.config.get('MAIL_USERNAME')}")
    print(f"MAIL_DEFAULT_SENDER: {app.config.get('MAIL_DEFAULT_SENDER')}")

    # Initialize scheduler with proper configuration
    if not scheduler.running:
        # Configure scheduler to use SQLAlchemy job store
        app.config['SCHEDULER_JOBSTORES'] = {
            'default': SQLAlchemyJobStore(url=app.config['SQLALCHEMY_DATABASE_URI'])
        }
        app.config['SCHEDULER_EXECUTORS'] = {
            'default': {'type': 'threadpool', 'max_workers': 1}
        }
        app.config['SCHEDULER_JOB_DEFAULTS'] = {
            'coalesce': True,
            'max_instances': 1,
            'replace_existing': True
        }
        app.config['SCHEDULER_API_ENABLED'] = False
        
        # Initialize and start scheduler
        scheduler.init_app(app)
        scheduler.start()
        app.logger.info("Scheduler initialized with SQLAlchemy job store")

    # Initialize CSRF protection
    csrf.init_app(app) 