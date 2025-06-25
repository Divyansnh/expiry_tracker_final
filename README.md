# Expiry Tracker

A comprehensive inventory management system with expiry date tracking, OCR capabilities, and automated notifications.

## Features

- Inventory management with expiry date tracking
- OCR-based expiry date extraction from images
- Email notifications for expiring items
- In-app notifications with status tracking
- Daily status updates and reports
- Integration with Zoho for inventory sync
- User authentication and authorization
- Responsive web interface
- Automated cleanup tasks
- Comprehensive documentation system

## Notification System

The system sends daily notifications at 9:11 PM BST about items that are expiring soon. The notification system includes:

- Duplicate prevention mechanisms
- Timezone-aware scheduling
- Cleanup tools for maintenance
- Monitoring capabilities

## Configuration

1. Copy `.env.example` to `.env` and fill in your configuration
2. Set up your database
3. Configure email settings for notifications
4. Set `WERKZEUG_RUN_MAIN=true` in your environment to prevent duplicate notifications

## Tech Stack

- **Backend**: Python, Flask 3.0.2
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **OCR**: Azure Computer Vision
- **Email**: SMTP (Gmail)
- **Authentication**: Flask-Login
- **API**: RESTful with Flask-CORS
- **Task Scheduling**: APScheduler
- **Development Tools**: Black, Flake8, MyPy
- **Data Analysis**: NumPy
- **Image Processing**: OpenCV

## Prerequisites

- Python 3.9+ (required for Flask 3.0.2)
- PostgreSQL
- Azure Computer Vision account
- Gmail account for email notifications
- Zoho account for inventory integration (optional)

## Installation

### Quick Setup (Recommended)

For new users, we provide automated setup scripts that handle the entire installation process:

```bash
# Clone the repository
git clone [repository-url]
cd expiry-tracker

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the automated setup script
python scripts/setup.py
# OR use the shell script
./scripts/setup.sh
```

The setup script will:
- ✅ Check Python version compatibility
- ✅ Install all dependencies
- ✅ Create necessary directories
- ✅ Set up environment configuration
- ✅ Initialize database and run migrations
- ✅ Provide clear next steps

**For detailed setup script documentation, see [scripts/README.md](scripts/README.md)**

### Verifying Setup Scripts

Before using the setup scripts, you can verify they work correctly:

```bash
# Quick verification (recommended)
python scripts/verify_setup.py

# Test without execution
python scripts/quick_test.py --dry-run

# Full testing in isolated environment
python scripts/quick_test.py
```

**For detailed verification guide, see [scripts/VERIFICATION_GUIDE.md](scripts/VERIFICATION_GUIDE.md)**

### Manual Installation

If you prefer to set up manually or the automated script doesn't work for your environment:

1. Clone the repository:
```bash
git clone [repository-url]
cd expiry-tracker
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit `.env` with your configuration:
```env
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/expiry_tracker

# Azure Computer Vision
AZURE_CV_KEY=your-azure-key
AZURE_CV_ENDPOINT=your-azure-endpoint

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Zoho Configuration (Optional)
ZOHO_CLIENT_ID=your-client-id
ZOHO_CLIENT_SECRET=your-client-secret
ZOHO_REDIRECT_URI=your-redirect-uri
```

5. Initialize the database:
```bash
flask db upgrade
```

## Usage

1. Start the development server:
```bash
flask run
# or
python run.py
```

2. Access the application at `http://localhost:5000`

3. Create an account and start managing your inventory

## Database Backup System

The application includes a comprehensive backup and restore system to protect your data.

### Quick Backup Operations

```bash
# Create backup
python scripts/backup/backup_db.py

# List backups
python scripts/backup/backup_db.py --list-backups

# Restore safely
python scripts/backup/backup_restore.py backup_file.backup.gz

# Set up automated backups
python scripts/backup/backup_scheduler.py --install-cron
```

### Backup Features

- **Automated backups** with compression and rotation
- **Safe restore operations** with validation and rollback
- **Scheduled backups** using cron jobs
- **Configuration management** for backup settings
- **Comprehensive logging** and monitoring

### Backup Safety

- Pre-restore backups created automatically
- File integrity validation
- Confirmation prompts for destructive operations
- Rollback capability if restore fails

**💾 Backup System Documentation:**
- **[scripts/backup/BACKUP_README.md](scripts/backup/BACKUP_README.md)** - Complete backup and restore system documentation

## Project Structure

```
expiry-tracker/
├── app/                    # Application code
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core functionality and middleware
│   ├── forms/             # Form definitions
│   ├── models/            # Database models
│   ├── routes/            # Route handlers
│   ├── services/          # Business logic
│   ├── static/            # Static files
│   ├── tasks/             # Scheduled tasks
│   ├── templates/         # HTML templates
│   ├── utils/             # Utility functions
│   ├── config.py          # Configuration
│   └── __init__.py        # Application factory
├── debug_images/          # OCR debug images
├── docs/                  # Documentation
├── logs/                  # Application logs
├── migrations/            # Database migrations
├── scripts/               # Setup and utility scripts
│   ├── README.md          # Main scripts overview
│   ├── backup/            # Database backup system
│   │   ├── backup_db.py   # Main backup script
│   │   ├── backup_restore.py # Safe restore script
│   │   ├── backup_scheduler.py # Automated scheduling
│   │   ├── backup_config.json # Backup configuration
│   │   └── BACKUP_README.md # Backup documentation
│   ├── setup/             # Project setup scripts
│   │   ├── setup.py       # Python setup script
│   │   ├── setup.sh       # Shell setup script
│   │   ├── quick_test.py  # Test script
│   │   ├── verify_setup.py # Verification script
│   │   ├── README.md      # Setup documentation
│   │   └── VERIFICATION_GUIDE.md # Testing guide
│   └── utils/             # Utility scripts (future use)
├── database_backups/      # Database backup storage (git-ignored)
├── test_images/          # Test images for OCR and processing
├── tests/                 # Test files
├── .env                   # Environment variables
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── LICENSE                # License file
└── run.py                 # Application entry point
```

## Documentation

Comprehensive documentation is available in the `docs/` directory:
- User guides
- API documentation
- Developer documentation
- Database schema
- Integration guides
- Security documentation
- Maintenance procedures
- Troubleshooting guides

**📚 For detailed documentation, see [docs/README.md](docs/README.md) which includes:**
- **User Guide** - Complete feature documentation and tutorials
- **API Documentation** - RESTful API endpoints and examples
- **Developer Guide** - Architecture, database schema, and development resources
- **Troubleshooting & Logging** - System monitoring and issue resolution
- **Security Documentation** - Implementation details and best practices
- **Getting Started** - Step-by-step setup and configuration guides

**🔧 Setup Scripts Documentation:**
- **[scripts/README.md](scripts/README.md)** - Complete setup script documentation and usage
- **[scripts/VERIFICATION_GUIDE.md](scripts/VERIFICATION_GUIDE.md)** - How to test and verify setup scripts

**💾 Backup System Documentation:**
- **[scripts/backup/BACKUP_README.md](scripts/backup/BACKUP_README.md)** - Complete backup and restore system documentation

## Development

The project uses several development tools to maintain code quality:

- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Static type checking

To run the development tools:

```bash
# Format code
black .

# Run linter
flake8

# Run type checking
mypy .
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Flask Framework
- Azure Computer Vision
- Zoho API
- All contributors and supporters 