# Scripts Directory

This directory contains organized utility scripts for the Expiry Tracker application.

## 📁 Directory Structure

```
scripts/
├── README.md              # This file - main scripts overview
├── backup/                # Database backup and restore system
│   ├── backup_db.py       # Main backup script
│   ├── backup_restore.py  # Safe restore script
│   ├── backup_scheduler.py # Automated backup scheduling
│   ├── backup_config.json # Backup configuration
│   └── BACKUP_README.md   # Complete backup documentation
├── setup/                 # Project setup and installation
│   ├── setup.py           # Python setup script
│   ├── setup.sh           # Shell setup script
│   ├── quick_test.py      # Test script
│   ├── verify_setup.py    # Verification script
│   ├── README.md          # Setup documentation
│   └── VERIFICATION_GUIDE.md # Testing guide
└── utils/                 # Utility scripts (future use)
```

## 🚀 Quick Start

### Database Backups
```bash
# Create backup
python scripts/backup/backup_db.py

# List backups
python scripts/backup/backup_db.py --list-backups

# Restore backup
python scripts/backup/backup_restore.py backup_file.backup.gz
```

### Project Setup
```bash
# Automated setup
python scripts/setup/setup.py

# Verify setup
python scripts/setup/verify_setup.py
```

## 📚 Documentation

### Backup System
- **[backup/BACKUP_README.md](backup/BACKUP_README.md)** - Complete backup and restore documentation
- Features: Automated backups, safe restore, scheduling, compression

### Setup System
- **[setup/README.md](setup/README.md)** - Setup script documentation
- **[setup/VERIFICATION_GUIDE.md](setup/VERIFICATION_GUIDE.md)** - Testing and verification guide
- Features: Automated installation, dependency management, database setup

## 🔧 Script Categories

### Backup Scripts (`backup/`)
- **backup_db.py** - Create database backups with compression
- **backup_restore.py** - Safe restore with validation and rollback
- **backup_scheduler.py** - Automated backup scheduling with cron
- **backup_config.json** - Backup configuration settings

### Setup Scripts (`setup/`)
- **setup.py** - Python-based project setup
- **setup.sh** - Shell-based project setup
- **quick_test.py** - Test script for verification
- **verify_setup.py** - Setup verification and testing

### Utility Scripts (`utils/`)
- Reserved for future utility scripts
- Database maintenance, cleanup, monitoring, etc.

## 🎯 Benefits of This Structure

- **Organized**: Scripts grouped by functionality
- **Maintainable**: Easy to find and update specific scripts
- **Scalable**: Easy to add new script categories
- **Documented**: Each category has its own documentation
- **Accessible**: Clear paths and usage examples

## 🔄 Migration Notes

If you have existing scripts or references, update the paths:

**Old paths:**
```bash
python scripts/backup_db.py
python scripts/setup.py
```

**New paths:**
```bash
python scripts/backup/backup_db.py
python scripts/setup/setup.py
```

## 📝 Adding New Scripts

When adding new scripts:

1. **Choose the appropriate category** (backup, setup, utils)
2. **Follow naming conventions** (descriptive names, .py extension)
3. **Add documentation** in the category's README
4. **Update this main README** if adding new categories

## 🛠️ Development

All scripts are designed to be:
- **Self-contained** - Minimal external dependencies
- **Configurable** - Use configuration files where appropriate
- **Safe** - Include validation and error handling
- **Documented** - Clear usage instructions and examples 