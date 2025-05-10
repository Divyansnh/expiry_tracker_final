# Expiry Tracker Documentation

A comprehensive inventory management system with expiry date tracking, OCR capabilities, and automated notifications.

## Core Features

### Inventory Management
- Track items with expiry dates
- Manage item quantities and units
- Monitor item status (active, expiring soon, expired)
- Bulk item operations
- Item categorization and organization

### OCR Date Extraction
- Extract expiry dates from product images
- Support for multiple date formats
- Image preprocessing for better accuracy
- Debug image storage for troubleshooting
- Multi-language support (English, French, Spanish)

### Notification System
- Daily email notifications at 3:45 PM BST
- Configurable notification preferences
- Duplicate prevention mechanisms
- Timezone-aware scheduling
- Notification history tracking
- Status monitoring and cleanup tools

### Zoho Books Integration
- Two-way inventory synchronization
- Automatic status updates
- Item creation and updates
- Expiry date tracking
- OAuth2 authentication
- Token refresh handling

## Technical Implementation

### Backend
- Python 3.9+ with Flask 3.0.2
- PostgreSQL database with SQLAlchemy 2.0
- RESTful API architecture
- APScheduler for task scheduling
- Flask-Login for authentication

### Frontend
- Responsive web interface
- Tailwind CSS for styling
- Real-time updates
- Interactive forms
- Image upload and processing

### External Services
- Azure Computer Vision for OCR
- SMTP (Gmail) for email notifications
- Zoho Books API for inventory sync

### Development Tools
- Black for code formatting
- Flake8 for linting
- MyPy for static type checking
- Pytest for testing with coverage
- Comprehensive logging system

## Project Structure

```
expiry-tracker/
├── app/                    # Application code
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core functionality
│   ├── forms/             # Form definitions
│   ├── middleware/        # Request/response middleware
│   ├── models/            # Database models
│   ├── repositories/      # Data access layer
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
├── scripts/               # Utility scripts
├── test_images/          # Test images for OCR
├── tests/                 # Test files
├── .env                   # Environment variables
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── LICENSE                # License file
├── README.md              # Main README
├── requirements.txt       # Python dependencies
└── run.py                 # Application entry point
```

## Configuration

The system requires several environment variables to be set:

```env
# Flask Configuration
FLASK_APP=app
FLASK_ENV=development
SECRET_KEY=your-secret-key

# Database Configuration
DATABASE_URL=postgresql://username:password@localhost:5432/expiry_tracker

# Azure Computer Vision
AZURE_VISION_KEY=your-azure-key
AZURE_VISION_ENDPOINT=your-azure-endpoint

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Zoho Configuration
ZOHO_CLIENT_ID=your-client-id
ZOHO_CLIENT_SECRET=your-client-secret
ZOHO_REDIRECT_URI=your-redirect-uri
```

## Documentation Sections

- [User Guide](user/getting-started.md) - Getting started and basic usage
- [API Documentation](api/README.md) - API endpoints and integration
- [Integration Guides](integrations/README.md) - External service integration
- [Maintenance](maintenance/notifications.md) - System maintenance and monitoring
- [Development](development/README.md) - Development setup and guidelines

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 