#!/usr/bin/env python3
import os
import sys
import logging
from pathlib import Path
from dotenv import load_dotenv

# Add the project root directory to the Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app
from app.core.extensions import db
from flask_migrate import upgrade

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_database():
    """Initialize and set up the database."""
    try:
        # Load environment variables
        load_dotenv()
        
        # Create Flask application
        app = create_app()
        
        with app.app_context():
            logger.info("Starting database setup...")
            
            # Check if database exists
            inspector = db.inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            if not existing_tables:
                logger.info("No existing tables found. Creating database tables...")
                db.create_all()
                
                # Run migrations if they exist
                if os.path.exists('migrations'):
                    logger.info("Running database migrations...")
                    upgrade()
                else:
                    logger.warning("No migrations directory found. Skipping migrations.")
            else:
                logger.info("Database tables already exist. Checking for pending migrations...")
                if os.path.exists('migrations'):
                    logger.info("Running any pending migrations...")
                    upgrade()
                else:
                    logger.warning("No migrations directory found. Skipping migrations.")
            
            logger.info("Database setup completed successfully!")
            
    except Exception as e:
        logger.error(f"Error during database setup: {str(e)}")
        sys.exit(1)

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY',
        'MAIL_SERVER',
        'MAIL_PORT',
        'MAIL_USERNAME',
        'MAIL_PASSWORD'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning("The following required environment variables are not set:")
        for var in missing_vars:
            logger.warning(f"- {var}")
        
        # Create .env file if it doesn't exist
        if not os.path.exists('.env'):
            logger.info("Creating .env file with default values...")
            with open('.env', 'w') as f:
                f.write("# Database Configuration\n")
                f.write("DATABASE_URL=postgresql://postgres:postgres@localhost:5432/expiry_tracker\n")
                f.write("\n# Security\n")
                f.write("SECRET_KEY=your-secret-key-here\n")
                f.write("\n# Email Configuration\n")
                f.write("MAIL_SERVER=smtp.gmail.com\n")
                f.write("MAIL_PORT=587\n")
                f.write("MAIL_USERNAME=your-email@gmail.com\n")
                f.write("MAIL_PASSWORD=your-app-password\n")
                f.write("\n# Optional Configuration\n")
                f.write("FLASK_ENV=development\n")
                f.write("DEBUG=True\n")
            
            logger.info("Please update the .env file with your actual configuration values.")
            sys.exit(1)
        else:
            logger.error("Please set the missing environment variables in your .env file.")
            sys.exit(1)

if __name__ == '__main__':
    logger.info("Starting database setup process...")
    
    # Check environment variables
    check_environment()
    
    # Setup database
    setup_database()
    
    logger.info("Database setup completed successfully!") 