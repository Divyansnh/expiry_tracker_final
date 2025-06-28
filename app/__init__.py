import logging
from logging.handlers import RotatingFileHandler
import os
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from app.config import config
from app.core.extensions import db, login_manager, jwt, migrate, cors, init_extensions, scheduler, mail
from app.core.errors import register_error_handlers
from app.core.middleware import log_request, handle_cors, validate_request
from app.routes import main_bp, auth_bp
from app.routes.reports import reports_bp
from app.routes.notifications import notifications_bp
from app.routes.activities import activities_bp
from app.api.v1 import api_bp
from app.tasks.cleanup import cleanup_expired_items, cleanup_unverified_accounts
from app.services.notification_service import NotificationService
from datetime import datetime

def create_app(config_name=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Determine which configuration to use
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # Load config
    app.config.from_object(config[config_name])
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        
        # Don't log sensitive configuration
        app.logger.info('Expiry Tracker startup')
        app.logger.info('Mail server configuration:')
        app.logger.info('MAIL_SERVER: %s', app.config.get('MAIL_SERVER'))
        app.logger.info('MAIL_PORT: %s', app.config.get('MAIL_PORT'))
        app.logger.info('MAIL_USE_TLS: %s', app.config.get('MAIL_USE_TLS'))
        app.logger.info('MAIL_USERNAME: %s', app.config.get('MAIL_USERNAME'))
        app.logger.info('MAIL_DEFAULT_SENDER: %s', app.config.get('MAIL_DEFAULT_SENDER'))
    
    # Initialize extensions
    init_extensions(app)
    
    # Only initialize scheduler if not in testing mode
    if not app.config.get('TESTING', False):
        app.logger.info("Checking scheduler initialization conditions...")
        app.logger.info(f"Testing mode: {app.config.get('TESTING', False)}")
        app.logger.info(f"WERKZEUG_RUN_MAIN: {os.environ.get('WERKZEUG_RUN_MAIN')}")
        app.logger.info(f"Process ID: {os.getpid()}")
        
        if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
            app.logger.info("Initializing scheduler in child process...")
            # Import task functions
            from app.tasks.scheduler_tasks import (
                cleanup_expired_task,
                cleanup_unverified_task,
                send_daily_notifications_task
            )
            
            # Add jobs with proper configuration
            try:
                scheduler.add_job(
                    id='cleanup_expired_items',
                    func=cleanup_expired_task,
                    trigger='cron',
                    hour=1,  # Midnight
                    minute=2,
                    timezone='Europe/London',
                    misfire_grace_time=60,  # Allow job to run up to 12 hours late
                    coalesce=True,  # Run missed jobs only once on startup
                    max_instances=1,  # Allow only one instance to run at a time
                    replace_existing=True  # Replace existing job if it exists
                )
                app.logger.info("Added cleanup_expired_items job")
            except Exception as e:
                app.logger.warning(f"Failed to add cleanup_expired_items job: {str(e)}")
            
            try:
                scheduler.add_job(
                    id='cleanup_unverified_accounts',
                    func=cleanup_unverified_task,
                    trigger='cron',
                    hour=21,  # Midnight
                    minute=13,
                    timezone='Europe/London',
                    misfire_grace_time=60,  # Allow job to run up to 12 hours late
                    coalesce=True,  # Run missed jobs only once on startup
                    max_instances=1,  # Allow only one instance to run at a time
                    replace_existing=True  # Replace existing job if it exists
                )
                app.logger.info("Added cleanup_unverified_accounts job")
            except Exception as e:
                app.logger.warning(f"Failed to add cleanup_unverified_accounts job: {str(e)}")
            
            try:
                scheduler.add_job(
                    id='send_daily_notifications',
                    func=send_daily_notifications_task,
                    trigger='cron',
                    hour=1,  # 1 AM BST
                    minute=1,
                    timezone='Europe/London',
                    misfire_grace_time=60,  # Allow job to run up to 12 hours late
                    coalesce=True,  # Run missed jobs only once on startup
                    max_instances=1,  # Allow only one instance to run at a time
                    replace_existing=True  # Replace existing job if it exists
                )
                app.logger.info("Added send_daily_notifications job")
            except Exception as e:
                app.logger.warning(f"Failed to add send_daily_notifications job: {str(e)}")
            
            # Log all scheduled jobs
            all_jobs = scheduler.get_jobs()
            app.logger.info("All scheduled jobs:")
            for job in all_jobs:
                app.logger.info(f"Job ID: {job.id}, Next Run: {job.next_run_time}")
    
    # Register error handlers
    register_error_handlers(app)
    
    # Register middleware
    log_request(app)
    handle_cors(app)
    validate_request(app)
    
    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(reports_bp)
    app.register_blueprint(notifications_bp)
    app.register_blueprint(activities_bp)
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app 