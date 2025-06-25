# Configuration Guide

This guide covers all configuration options for the Expiry Tracker application, including environment variables, database settings, and external service integrations.

## Environment Variables

Create a `.env` file in the root directory with the following variables:

### Database Configuration

```bash
# Database URL (PostgreSQL recommended)
DATABASE_URL=postgresql://username:password@localhost:5432/expiry_tracker

# Alternative: Individual database settings
DB_HOST=localhost
DB_PORT=5432
DB_NAME=expiry_tracker
DB_USER=your_username
DB_PASSWORD=your_password
```

### Flask Configuration

```bash
# Flask secret key (generate with: python -c "import secrets; print(secrets.token_hex(32))")
SECRET_KEY=your-secret-key-here

# Flask environment
FLASK_ENV=development  # or production
FLASK_DEBUG=True  # Set to False in production

# Session configuration
SESSION_COOKIE_SECURE=False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

### Email Configuration (Gmail)

```bash
# SMTP Settings
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Note: Use App Password, not regular password for Gmail
```

### Azure Computer Vision (OCR)

```bash
# Azure Computer Vision credentials
AZURE_VISION_KEY=your-azure-vision-key
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
```

### Zoho Integration

```bash
# Zoho API credentials
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REDIRECT_URI=http://localhost:5000/auth/zoho/callback
ZOHO_ORGANIZATION_ID=your-organization-id

# Zoho API endpoints (usually don't need to change)
ZOHO_ACCESS_TOKEN_URL=https://accounts.zoho.eu/oauth/v2/token
ZOHO_AUTHORIZE_URL=https://accounts.zoho.eu/oauth/v2/auth
ZOHO_API_BASE_URL=https://www.zohoapis.eu/inventory/v1
ZOHO_ACCOUNTS_URL=https://accounts.zoho.eu
```

### Security Settings

```bash
# Account lockout
MAX_LOGIN_ATTEMPTS=5
LOCKOUT_DURATION_MINUTES=15

# Session and verification timeouts
PASSWORD_RESET_EXPIRY=15  # minutes
EMAIL_VERIFICATION_EXPIRY=5  # minutes
VERIFICATION_CODE_EXPIRY=5  # minutes
```

### Production Settings

```bash
# Production-specific settings
WERKZEUG_RUN_MAIN=true  # Prevents duplicate notifications
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## Configuration Classes

The application uses different configuration classes for different environments:

### Development Configuration

```python
class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
```

### Production Configuration

```python
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Strict'
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'max_overflow': 10
    }
```

## External Service Setup

### Gmail App Password Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Use the generated password** in `MAIL_PASSWORD`

### Azure Computer Vision Setup

1. **Create Azure Resource**:
   - Go to Azure Portal
   - Create Computer Vision resource
   - Choose region and pricing tier
2. **Get Credentials**:
   - Copy the endpoint URL
   - Copy the key from "Keys and Endpoint"
3. **Configure Environment**:
   - Set `AZURE_VISION_KEY`
   - Set `AZURE_VISION_ENDPOINT`

### Zoho Developer Console Setup

1. **Create Zoho App**:
   - Go to Zoho Developer Console
   - Create new client
   - Set redirect URI
2. **Get Credentials**:
   - Copy Client ID
   - Copy Client Secret
3. **Configure Scopes**:
   - Add `ZohoInventory.FullAccess.all` scope

## Database Configuration

### PostgreSQL Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb expiry_tracker

# Create user
sudo -u postgres createuser --interactive

# Grant privileges
sudo -u postgres psql
GRANT ALL PRIVILEGES ON DATABASE expiry_tracker TO your_username;
```

### Database Migration

```bash
# Initialize migrations
flask db init

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migrations
flask db upgrade
```

## Scheduled Tasks

The application runs several automated tasks:

### Daily Notifications
- **Time**: 9:11 PM BST (21:11 UTC)
- **Purpose**: Send daily inventory status updates
- **Configuration**: Hardcoded in scheduler

### Cleanup Tasks
- **Expired Items**: 1:02 AM BST (01:02 UTC)
- **Unverified Accounts**: 9:13 PM BST (21:13 UTC)

## Validation

After configuration, validate your setup:

```bash
# Test database connection
flask db current

# Test email configuration
python -c "
from app import create_app
from app.services.email_service import EmailService
app = create_app()
with app.app_context():
    service = EmailService()
    print('Email service initialized successfully')
"

# Test Azure OCR
curl -X GET "http://localhost:5000/api/v1/date_ocr/test"
```

## Troubleshooting

### Common Issues

1. **Database Connection Failed**:
   - Check `DATABASE_URL` format
   - Verify PostgreSQL service is running
   - Ensure database exists and user has permissions

2. **Email Configuration Error**:
   - Verify Gmail app password is correct
   - Check 2FA is enabled on Gmail account
   - Ensure SMTP settings are correct

3. **Azure Vision Error**:
   - Verify credentials are correct
   - Check Azure service is active
   - Ensure endpoint URL is complete

4. **Zoho Integration Error**:
   - Verify OAuth credentials
   - Check redirect URI matches exactly
   - Ensure proper scopes are configured

### Environment-Specific Issues

#### Windows
- Use `venv\Scripts\activate` to activate virtual environment
- Install Visual C++ Build Tools if you encounter compilation errors

#### macOS
- Install PostgreSQL using Homebrew: `brew install postgresql`
- Start PostgreSQL: `brew services start postgresql`

#### Linux (Ubuntu/Debian)
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3-dev libpq-dev postgresql postgresql-contrib

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

## Security Best Practices

### Production Deployment
- Use strong, unique `SECRET_KEY`
- Enable HTTPS and set `SESSION_COOKIE_SECURE=True`
- Use environment variables for all sensitive data
- Regularly update dependencies
- Monitor application logs

### Database Security
- Use dedicated database user with minimal privileges
- Enable SSL connections for database
- Regularly backup database
- Monitor database access logs

### Email Security
- Use app passwords instead of regular passwords
- Enable 2FA on email accounts
- Monitor email sending logs
- Use dedicated email for notifications

## Next Steps

After configuration:

1. **Test the Application** - Verify all features work correctly
2. **Set up Monitoring** - Configure logging and alerts
3. **Create Backup Strategy** - Set up database backups
4. **Review Security** - Ensure all security measures are in place

---

**Previous**: [Installation Guide](./installation.md) | **Next**: [First Steps](./first-steps.md) 