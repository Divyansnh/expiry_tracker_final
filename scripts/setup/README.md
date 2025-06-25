# Setup Scripts

This directory contains setup scripts to help new users get started with the Expiry Tracker Flask application after cloning the repository.

## Available Scripts

### 1. `setup.py` - Python Setup Script

A comprehensive Python script that handles the complete setup process.

**Features:**
- Environment validation (Python version, virtual environment)
- Dependency installation
- Environment file creation
- Directory structure setup
- Database initialization and migrations
- Detailed error reporting and logging

**Usage:**
```bash
# Run complete setup
python scripts/setup.py

# Skip database setup
python scripts/setup.py --skip-db

# Force database operations
python scripts/setup.py --force

# Enable verbose logging
python scripts/setup.py --verbose

# Show help
python scripts/setup.py --help
```

### 2. `setup.sh` - Shell Setup Script

A bash script alternative for users who prefer shell scripts.

**Features:**
- Colored output for better readability
- Cross-platform compatibility
- Same functionality as the Python script
- Lightweight and fast

**Usage:**
```bash
# Run complete setup
./scripts/setup.sh

# Skip database setup
./scripts/setup.sh --skip-db

# Enable verbose output
./scripts/setup.sh --verbose

# Show help
./scripts/setup.sh --help
```

## What the Setup Scripts Do

### Environment Setup
1. **Python Version Check**: Ensures Python 3.8+ is installed
2. **Virtual Environment Check**: Warns if not using a virtual environment
3. **Dependency Installation**: Installs all packages from `requirements.txt`
4. **Environment File Creation**: Creates `.env` file from `.env.example` or generates a basic one
5. **Directory Creation**: Creates necessary directories for the application

### Database Setup
1. **Connection Test**: Verifies database connection is configured
2. **Migration Initialization**: Creates initial migration if needed
3. **Migration Execution**: Runs all pending database migrations
4. **Table Creation**: Creates database tables if they don't exist

### Created Directories
- `logs/` - Application log files
- `app/static/uploads/` - File uploads
- `app/flask_session/` - Flask session files
- `debug_images/` - Debug images for OCR processing
- `test_images/` - Test images
- `oauth_states/` - OAuth state management

## Prerequisites

Before running the setup scripts, ensure you have:

1. **Python 3.8+** installed
2. **Git** installed (to clone the repository)
3. **Database** configured (PostgreSQL recommended)
4. **Virtual environment** (recommended but not required)

## Quick Start

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd expiry-tracker
   ```

2. **Create and activate virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Run the setup script:**
   ```bash
   # Using Python script
   python scripts/setup.py
   
   # Or using shell script
   ./scripts/setup.sh
   ```

4. **Update configuration:**
   - Edit the `.env` file with your actual configuration
   - Set up your database connection
   - Configure email settings (optional)
   - Add Zoho credentials (optional)
   - Add Azure Computer Vision credentials (optional)

5. **Start the application:**
   ```bash
   python run.py
   ```

6. **Access the application:**
   - Open your browser and go to: http://localhost:5000

## Troubleshooting

### Common Issues

1. **Database Connection Failed**
   - Ensure your database is running
   - Check the `DATABASE_URL` in your `.env` file
   - Verify database credentials

2. **Dependencies Installation Failed**
   - Make sure you're in a virtual environment
   - Check your internet connection
   - Try upgrading pip: `pip install --upgrade pip`

3. **Migration Errors**
   - Ensure database is accessible
   - Check if migrations directory exists
   - Try running `flask db upgrade` manually

4. **Permission Errors (Shell Script)**
   - Make the script executable: `chmod +x scripts/setup.sh`
   - Run with proper permissions

### Manual Setup

If the setup scripts fail, you can perform the setup manually:

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment:**
   ```bash
   cp .env.example .env  # If .env.example exists
   # Edit .env with your configuration
   ```

3. **Initialize database:**
   ```bash
   flask db upgrade
   ```

4. **Create directories:**
   ```bash
   mkdir -p logs app/static/uploads app/flask_session debug_images test_images oauth_states
   ```

## Configuration

The setup scripts will create a `.env` file with the following configuration options:

### Required Configuration
- `SECRET_KEY` - Flask secret key
- `DATABASE_URL` - Database connection string

### Optional Configuration
- `MAIL_*` - Email settings for notifications
- `ZOHO_*` - Zoho integration settings
- `AZURE_VISION_*` - Azure Computer Vision settings

## Support

If you encounter issues with the setup scripts:

1. Check the error messages for specific issues
2. Verify all prerequisites are met
3. Try running the script with `--verbose` flag for more details
4. Check the main README.md for additional information
5. Open an issue on the repository with detailed error information

## Notes

- The setup scripts are designed to be idempotent - you can run them multiple times safely
- Database setup can be skipped if you want to configure it manually later
- The scripts will create a basic `.env` file if `.env.example` doesn't exist
- All created directories are added to `.gitignore` to prevent committing sensitive data 