#!/usr/bin/env python3
"""
Setup script for Expiry Tracker Flask Application

This script helps new users set up the application after cloning the repository.
It handles database initialization, environment setup, and provides clear instructions.

Usage:
    python scripts/setup.py
    python scripts/setup.py --help
    python scripts/setup.py --skip-db
    python scripts/setup.py --force
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SetupError(Exception):
    """Custom exception for setup errors."""
    pass

class DatabaseSetup:
    """Handles database initialization and migrations."""
    
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.migrations_dir = app_root / "migrations"
        
    def check_database_connection(self) -> bool:
        """Check if database connection is configured."""
        try:
            # Try to import and create app to test database connection
            sys.path.insert(0, str(self.app_root))
            from app import create_app
            from app.core.extensions import db
            
            app = create_app('development')
            with app.app_context():
                # Test database connection
                with db.engine.connect() as connection:
                    connection.execute(db.text("SELECT 1"))
                logger.info("✓ Database connection successful")
                return True
        except Exception as e:
            logger.error(f"✗ Database connection failed: {e}")
            return False
    
    def run_migrations(self) -> bool:
        """Run database migrations."""
        try:
            logger.info("Running database migrations...")
            
            # Change to app root directory
            original_cwd = os.getcwd()
            os.chdir(self.app_root)
            
            # Run migrations
            result = subprocess.run(
                ["flask", "db", "upgrade"],
                capture_output=True,
                text=True,
                check=True
            )
            
            logger.info("✓ Database migrations completed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Migration failed: {e}")
            logger.error(f"Migration output: {e.stdout}")
            logger.error(f"Migration error: {e.stderr}")
            return False
        except FileNotFoundError:
            logger.error("✗ Flask CLI not found. Make sure Flask is installed.")
            return False
        finally:
            os.chdir(original_cwd)
    
    def create_tables(self) -> bool:
        """Create database tables if they don't exist."""
        try:
            logger.info("Creating database tables...")
            
            sys.path.insert(0, str(self.app_root))
            from app import create_app
            from app.core.extensions import db
            
            app = create_app('development')
            with app.app_context():
                db.create_all()
                logger.info("✓ Database tables created successfully")
                return True
                
        except Exception as e:
            logger.error(f"✗ Failed to create tables: {e}")
            return False
    
    def initialize_database(self, force: bool = False) -> bool:
        """Initialize the database with tables and migrations."""
        logger.info("=== Database Setup ===")
        
        # Check if database connection is configured
        if not self.check_database_connection():
            logger.error("Please configure your database connection first.")
            logger.error("Set the DATABASE_URL environment variable or update app/config.py")
            return False
        
        # Check if migrations directory exists
        if not self.migrations_dir.exists():
            logger.warning("Migrations directory not found. Creating initial migration...")
            try:
                os.chdir(self.app_root)
                subprocess.run(["flask", "db", "init"], check=True, capture_output=True)
                subprocess.run(["flask", "db", "migrate", "-m", "Initial migration"], check=True, capture_output=True)
                logger.info("✓ Initial migration created")
            except subprocess.CalledProcessError as e:
                logger.error(f"✗ Failed to create initial migration: {e}")
                return False
        
        # Run migrations
        if not self.run_migrations():
            return False
        
        # Create tables if needed
        if not self.create_tables():
            return False
        
        logger.info("✓ Database setup completed successfully")
        return True

class EnvironmentSetup:
    """Handles environment setup and validation."""
    
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.env_file = app_root / ".env"
        self.env_example_file = app_root / ".env.example"
    
    def check_python_version(self) -> bool:
        """Check if Python version is compatible."""
        if sys.version_info < (3, 8):
            logger.error(f"✗ Python 3.8+ required. Current version: {sys.version}")
            return False
        logger.info(f"✓ Python version {sys.version_info.major}.{sys.version_info.minor} is compatible")
        return True
    
    def check_virtual_environment(self) -> bool:
        """Check if running in a virtual environment."""
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            logger.info("✓ Running in virtual environment")
            return True
        else:
            logger.warning("⚠ Not running in virtual environment")
            logger.warning("It's recommended to use a virtual environment")
            return False
    
    def install_dependencies(self) -> bool:
        """Install Python dependencies."""
        try:
            logger.info("Installing Python dependencies...")
            
            requirements_file = self.app_root / "requirements.txt"
            if not requirements_file.exists():
                logger.error(f"✗ Requirements file not found: {requirements_file}")
                return False
            
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            
            logger.info("✓ Dependencies installed successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install dependencies: {e}")
            return False
    
    def create_env_file(self) -> bool:
        """Create .env file from example if it doesn't exist."""
        if self.env_file.exists():
            logger.info("✓ .env file already exists")
            return True
        
        if self.env_example_file.exists():
            logger.info("Creating .env file from .env.example...")
            try:
                import shutil
                shutil.copy(self.env_example_file, self.env_file)
                logger.info("✓ .env file created from .env.example")
                logger.warning("⚠ Please update .env file with your actual configuration")
                return True
            except Exception as e:
                logger.error(f"✗ Failed to create .env file: {e}")
                return False
        else:
            logger.warning("⚠ No .env.example file found")
            logger.info("Creating basic .env file...")
            try:
                self._create_basic_env_file()
                logger.info("✓ Basic .env file created")
                logger.warning("⚠ Please update .env file with your configuration")
                return True
            except Exception as e:
                logger.error(f"✗ Failed to create .env file: {e}")
                return False
    
    def _create_basic_env_file(self):
        """Create a basic .env file with common settings."""
        env_content = """# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database Configuration
DATABASE_URL=postgresql://localhost/expiry_tracker_v2

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Zoho Configuration (Optional)
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REDIRECT_URI=http://localhost:5000/auth/zoho/callback
ZOHO_ORGANIZATION_ID=your-zoho-org-id

# Azure Computer Vision (Optional)
AZURE_VISION_KEY=your-azure-vision-key
AZURE_VISION_ENDPOINT=your-azure-vision-endpoint
"""
        with open(self.env_file, 'w') as f:
            f.write(env_content)
    
    def create_directories(self) -> bool:
        """Create necessary directories."""
        try:
            directories = [
                "logs",
                "app/static/uploads",
                "app/flask_session",
                "debug_images",
                "test_images",
                "oauth_states"
            ]
            
            for directory in directories:
                dir_path = self.app_root / directory
                dir_path.mkdir(parents=True, exist_ok=True)
            
            logger.info("✓ Required directories created")
            return True
            
        except Exception as e:
            logger.error(f"✗ Failed to create directories: {e}")
            return False
    
    def setup_environment(self) -> bool:
        """Set up the environment for the application."""
        logger.info("=== Environment Setup ===")
        
        # Check Python version
        if not self.check_python_version():
            return False
        
        # Check virtual environment
        self.check_virtual_environment()
        
        # Install dependencies
        if not self.install_dependencies():
            return False
        
        # Create .env file
        if not self.create_env_file():
            return False
        
        # Create directories
        if not self.create_directories():
            return False
        
        logger.info("✓ Environment setup completed successfully")
        return True

class SetupManager:
    """Main setup manager class."""
    
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.db_setup = DatabaseSetup(app_root)
        self.env_setup = EnvironmentSetup(app_root)
    
    def run_setup(self, skip_db: bool = False, force: bool = False) -> bool:
        """Run the complete setup process."""
        logger.info("🚀 Starting Expiry Tracker Setup")
        logger.info(f"Application root: {self.app_root}")
        
        try:
            # Environment setup
            if not self.env_setup.setup_environment():
                return False
            
            # Database setup (optional)
            if not skip_db:
                if not self.db_setup.initialize_database(force=force):
                    return False
            else:
                logger.info("⏭ Skipping database setup as requested")
            
            self._print_success_message()
            return True
            
        except Exception as e:
            logger.error(f"✗ Setup failed with error: {e}")
            return False
    
    def _print_success_message(self):
        """Print success message with next steps."""
        logger.info("")
        logger.info("🎉 Setup completed successfully!")
        logger.info("")
        logger.info("Next steps:")
        logger.info("1. Update your .env file with your actual configuration")
        logger.info("2. Start the application: python run.py")
        logger.info("3. Open your browser and go to: http://localhost:5000")
        logger.info("")
        logger.info("For more information, see the README.md file")
        logger.info("")

def main():
    """Main entry point for the setup script."""
    parser = argparse.ArgumentParser(
        description="Setup script for Expiry Tracker Flask Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/setup.py              # Run complete setup
  python scripts/setup.py --skip-db    # Skip database setup
  python scripts/setup.py --force      # Force database operations
  python scripts/setup.py --help       # Show this help message
        """
    )
    
    parser.add_argument(
        '--skip-db',
        action='store_true',
        help='Skip database initialization and migrations'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Force database operations (use with caution)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get application root
    script_dir = Path(__file__).parent
    app_root = script_dir.parent
    
    # Validate app root
    if not (app_root / "app").exists():
        logger.error("✗ Invalid application root. Make sure you're running this from the project directory.")
        sys.exit(1)
    
    # Run setup
    setup_manager = SetupManager(app_root)
    success = setup_manager.run_setup(skip_db=args.skip_db, force=args.force)
    
    if not success:
        logger.error("✗ Setup failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main() 