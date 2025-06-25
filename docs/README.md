# Expiry Tracker - Complete Documentation

## Overview

Expiry Tracker is a comprehensive inventory management system designed to help businesses and individuals track product expiry dates, manage inventory efficiently, and prevent losses due to expired items. The system provides automated notifications, detailed reporting, and integration with external services.

## Quick Links

- **[Main Project README](../README.md)** - Project overview, quick start, and installation guide
- **[Getting Started Guide](./getting-started/README.md)** - Step-by-step setup instructions
- **[User Guide](./user-guide/README.md)** - Complete feature documentation
- **[API Documentation](./api/README.md)** - RESTful API reference
- **[Developer Guide](./developer/README.md)** - Technical documentation and architecture

## Table of Contents

### 1. [Getting Started](./getting-started/README.md)
- [Installation Guide](./getting-started/installation.md)
- [Configuration](./getting-started/configuration.md)
- [First Steps](./getting-started/first-steps.md)

### 2. [User Guide](./user-guide/README.md)
- [Dashboard Overview](./user-guide/dashboard.md)
- [Inventory Management](./user-guide/inventory.md)
- [Notifications](./user-guide/notifications.md)
- [Reports](./user-guide/reports.md)
- [Settings](./user-guide/settings.md)
- [Activities](./user-guide/activities.md)

### 3. [API Documentation](./api/README.md)
- [Authentication](./api/authentication.md)
- [Items API](./api/items.md)
- [Reports API](./api/reports.md)
- [Notifications API](./api/notifications.md)
- [Settings API](./api/settings.md)
- [Activities API](./api/activities.md)
- [Date OCR API](./api/date-ocr.md)

### 4. [Developer Guide](./developer/README.md)
- [Architecture Overview](./developer/architecture.md)
- [Database Schema](./developer/database.md)
- [Services Layer](./developer/services.md)
- [Models](./developer/models.md)
- [Security Implementation](./developer/security.md)
- [Security Implementation Details](./developer/security-implementation.md)
- [Troubleshooting & Logging Guide](./developer/troubleshooting-logging.md)
- [Logging Quick Reference](./developer/logging-quick-reference.md)

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Initialize Database**
   ```bash
   flask db upgrade
   ```

4. **Run Application**
   ```bash
   python run.py
   ```

## Key Features

### ✅ Fully Implemented & Working

- **User Authentication & Authorization**
  - Secure login/registration with email verification
  - Password reset functionality
  - Account lockout protection
  - Session management

- **Inventory Management**
  - Add, edit, delete inventory items
  - Bulk operations (delete)
  - Real-time status tracking
  - Search and filtering
  - Image upload with OCR date extraction

- **Notification System**
  - Email notifications for expiring items
  - In-app notification management
  - Duplicate prevention

- **Reporting System**
  - Daily automated reports
  - Historical comparison
  - Risk analysis and scoring
  - Detailed item analysis

- **Zoho Integration**
  - Secure credential management
  - Two-way inventory synchronization
  - OAuth2 authentication
  - Encrypted credential storage

- **Activity Tracking**
  - Complete audit trail
  - User activity logging
  - System event tracking
  - Activity history

- **Security Features**
  - CSRF protection
  - XSS prevention
  - SQL injection protection
  - Password hashing with bcrypt
  - Input validation and sanitization

- **Comprehensive Logging System**
  - Application event logging
  - HTTP access logging
  - Credential access audit trail
  - Error tracking and monitoring
  - User activity database logging
  - Log rotation and maintenance

## Technology Stack

- **Backend**: Python 3.9+, Flask 3.0.2
- **Database**: PostgreSQL with SQLAlchemy 2.0
- **Frontend**: HTML5, CSS3, JavaScript, Tailwind CSS
- **OCR**: Azure Computer Vision
- **Email**: SMTP (Gmail)
- **Authentication**: Flask-Login, JWT
- **Task Scheduling**: APScheduler
- **Security**: bcrypt, CSRF tokens, input validation

## Support

For technical support or questions:
- Check the [User Guide](./user-guide/README.md) for feature documentation
- Review the [Getting Started](./getting-started/README.md) for setup help
- Contact the development team

## License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Last Updated**: June 2025  
**Version**: 1.0.0  
**Status**: Production 