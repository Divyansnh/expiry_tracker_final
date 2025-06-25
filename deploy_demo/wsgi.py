import os
import logging
from app import create_app
from app.core.extensions import db
from flask_migrate import upgrade

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = create_app('production')

def init_db():
    """Initialize the database."""
    with app.app_context():
        try:
            logger.info("Checking database tables...")
            db.create_all()
            if os.path.exists('migrations'):
                logger.info("Running database migrations...")
                upgrade()
            logger.info("Database initialization complete")
        except Exception as e:
            logger.error(f"Error during database initialization: {str(e)}")
            raise

if __name__ == '__main__':
    logger.info("Starting production application...")
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
else:
    # Initialize database when imported as WSGI app
    init_db() 