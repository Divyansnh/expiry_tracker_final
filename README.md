# Expiry Tracker

A comprehensive inventory management system with expiry date tracking, OCR capabilities, and automated notifications.

## Features

- Inventory management with expiry date tracking
- OCR-based expiry date extraction from images
- Email notifications for expiring items
- In-app notifications with status tracking
- Daily status updates and reports
- Integration with Zoho for inventory sync
- Analytics and reporting with public sharing
- User authentication and authorization
- Responsive web interface
- Automated cleanup tasks
- Backup and restore functionality
- Comprehensive documentation system

## Notification System

The system sends daily notifications at 3:45 PM BST about items that are expiring soon. The notification system includes:

- Duplicate prevention mechanisms
- Timezone-aware scheduling
- Cleanup tools for maintenance
- Monitoring capabilities

For detailed information about the notification system, see [docs/maintenance/notifications.md](docs/maintenance/notifications.md).

## Configuration

1. Copy `.env.example` to `.env` and fill in your configuration
2. Set up your database
3. Configure email settings for notifications
4. Set `WERKZEUG_RUN_MAIN=true` in your environment to prevent duplicate notifications

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript, Tailwind CSS
- **Database**: PostgreSQL
- **OCR**: Azure Computer Vision
- **Email**: SMTP (Gmail)
- **Authentication**: Flask-Login, JWT
- **API**: RESTful
- **Task Scheduling**: APScheduler
- **Documentation**: Markdown

## Prerequisites

- Python 3.8+
- PostgreSQL
- Azure Computer Vision account
- Gmail account for email notifications
- Zoho account for inventory integration (optional)

## Installation

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
├── backups/               # Database backups
├── config/                # Configuration files
├── debug_images/          # OCR debug images
├── docs/                  # Documentation
├── logs/                  # Application logs
├── migrations/            # Database migrations
├── scripts/               # Utility scripts
├── tests/                 # Test files
├── .env                   # Environment variables
├── .env.example           # Example environment variables
├── .gitignore             # Git ignore file
├── LICENSE                # License file
├── README.md              # This file
├── requirements.txt       # Python dependencies
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