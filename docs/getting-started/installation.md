# Installation Guide

This guide will walk you through installing and setting up the Expiry Tracker application on your local machine.

## Prerequisites

Before installing the application, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://www.postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/expiry-tracker.git
cd expiry-tracker
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 4. Database Setup

#### PostgreSQL Setup

1. **Create Database**
   ```bash
   # Connect to PostgreSQL
   psql -U postgres
   
   # Create database and user
   CREATE DATABASE expiry_tracker;
   CREATE USER expiry_user WITH PASSWORD 'your_secure_password';
   GRANT ALL PRIVILEGES ON DATABASE expiry_tracker TO expiry_user;
   \q
   ```

2. **Initialize Database**
   ```bash
   # Initialize database tables
   flask db upgrade
   ```

### 5. Environment Configuration

1. **Copy Environment Template**
   ```bash
   cp .env.example .env
   ```

2. **Edit Environment Variables**
   ```bash
   # Open .env file in your preferred editor
   nano .env
   ```

3. **Configure Required Variables**
   ```env
   # Flask Configuration
   SECRET_KEY=your-super-secret-key-here
   FLASK_ENV=development
   
   # Database Configuration
   DATABASE_URL=postgresql://expiry_user:your_secure_password@localhost/expiry_tracker
   # OR for SQLite: DATABASE_URL=sqlite:///app.db
   
   # Email Configuration
   MAIL_SERVER=smtp.gmail.com
   MAIL_PORT=587
   MAIL_USE_TLS=true
   MAIL_USERNAME=your-email@gmail.com
   MAIL_PASSWORD=your-app-password
   MAIL_DEFAULT_SENDER=your-email@gmail.com
   
   # Azure Computer Vision (for OCR)
   AZURE_VISION_KEY=your-azure-vision-key
   AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/
   
   # Zoho Integration (optional)
   ZOHO_CLIENT_ID=your-zoho-client-id
   ZOHO_CLIENT_SECRET=your-zoho-client-secret
   ZOHO_REDIRECT_URI=http://localhost:5000/auth/zoho/callback
   ```

### 6. Create Admin User (Optional)

```bash
# Run the application
python run.py

# Access the registration page at http://localhost:5000/auth/register
# Or create admin user programmatically:
python -c "
from app import create_app
from app.models.user import User
from app.core.extensions import db

app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com')
    admin.set_password('secure_password_123')
    admin.email_verified = True
    db.session.add(admin)
    db.session.commit()
    print('Admin user created successfully')
"
```

## Verification

### 1. Application Test

1. **Start the Application**
   ```bash
   python run.py
   ```

2. **Access the Application**
   - Open browser: `http://localhost:5000`
   - Verify the home page loads correctly

3. **Test Registration**
   - Navigate to registration page
   - Create a test account
   - Verify email verification works

4. **Test Basic Functionality**
   - Login with your account
   - Add a test item to inventory
   - Generate a report
   - Check notifications

### 2. Database Verification

```bash
# Connect to database and verify tables
psql -U expiry_user -d expiry_tracker -c "\dt"

# Expected output should show tables:
# users, items, activities, notifications, reports
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error
```
Error: (psycopg2.OperationalError) could not connect to server
```

**Solution:**
- Verify PostgreSQL is running
- Check database credentials in `.env`
- Ensure database exists

#### 2. Import Error
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
- Activate virtual environment
- Reinstall requirements: `pip install -r requirements.txt`

#### 3. Azure Vision Error
```
Error: Azure Computer Vision credentials not found
```

**Solution:**
- Verify AZURE_VISION_KEY and AZURE_VISION_ENDPOINT in `.env`
- Check Azure portal for correct credentials

#### 4. Email Configuration Error
```
Error: SMTP authentication failed
```

**Solution:**
- Verify email credentials in `.env`
- For Gmail, use App Password instead of regular password
- Check if 2FA is enabled on email account

#### 5. Zoho Integration Error
```
Error: Zoho credentials not found
```

**Solution:**
- Verify ZOHO_CLIENT_ID and ZOHO_CLIENT_SECRET in `.env`
- Check Zoho Developer Console for correct credentials

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

## Next Steps

After successful installation:

1. **Read the User Guide** - Learn how to use the application
2. **Configure Email** - Set up email notifications
3. **Set up Zoho Integration** - Connect with Zoho CRM (optional)
4. **Add Inventory Items** - Start managing your inventory
5. **Generate Reports** - Create your first inventory report

## Support

If you encounter issues during installation:

1. **Check this documentation** for solutions
2. **Review troubleshooting guides**
3. **Check application logs** for error details
4. **Contact support** with specific error messages

---

**Previous**: [Getting Started Overview](./README.md) | **Next**: [Configuration Guide](./configuration.md) 