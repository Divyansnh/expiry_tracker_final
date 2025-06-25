# Developer Documentation

## Overview

This section contains comprehensive technical documentation for developers working on the Expiry Tracker application. It covers the architecture, database design, services layer, models, and security implementation.

## Table of Contents

### 1. [Architecture Overview](./architecture.md)
- Application structure and design patterns
- Flask application organization
- Blueprint architecture
- Middleware and extensions
- Request/response flow

### 2. [Database Schema](./database.md)
- Database design and relationships
- Migration system (Alembic)
- Table structures and constraints
- Indexing strategies
- Data integrity rules

### 3. [Services Layer](./services.md)
- Business logic implementation
- External service integrations
- Email service configuration
- Zoho CRM integration
- Notification service architecture
- Task scheduling with APScheduler

### 4. [Models](./models.md)
- SQLAlchemy model definitions
- User management models
- Inventory and item models
- Notification and report models
- Activity tracking models
- Model relationships and constraints

### 5. [Security Implementation](./security.md)
- Authentication and authorization
- Password security (bcrypt)
- CSRF protection
- Input validation and sanitization
- XSS and SQL injection prevention
- Session management

### 6. [Security Implementation Details](./security-implementation.md)
- Detailed security configurations
- Credential encryption
- Access control mechanisms
- Security best practices
- Vulnerability prevention

### 7. [Troubleshooting & Logging Guide](./troubleshooting-logging.md)
- Comprehensive logging system documentation
- Log file structure and categories
- Troubleshooting common issues
- Performance monitoring and analysis
- Security and audit trail information

### 8. [Logging Quick Reference](./logging-quick-reference.md)
- Essential monitoring commands
- Common troubleshooting shortcuts
- Performance analysis tools
- Maintenance and backup procedures
- Environment-specific commands

## Quick Reference

### Key Technologies
- **Framework**: Flask 3.0.2
- **ORM**: SQLAlchemy 2.0
- **Database**: PostgreSQL
- **Authentication**: Flask-Login
- **Security**: bcrypt, CSRF tokens
- **Task Scheduling**: APScheduler
- **Email**: SMTP (Gmail)
- **OCR**: Azure Computer Vision

### Project Structure
```
app/
├── api/v1/          # API endpoints
├── core/            # Core extensions and middleware
├── models/          # Database models
├── routes/          # Web routes and views
├── services/        # Business logic services
├── templates/       # Jinja2 templates
├── utils/           # Utility functions
└── forms/           # WTForms definitions
```

### Development Workflow

1. **Database Changes**
   ```bash
   # Create new migration
   flask db migrate -m "Description of changes"
   
   # Apply migrations
   flask db upgrade
   ```

2. **Adding New Features**
   - Create models in `app/models/`
   - Add services in `app/services/`
   - Create routes in `app/routes/` or API in `app/api/v1/`
   - Add templates in `app/templates/`

3. **Security Considerations**
   - Always validate and sanitize input
   - Use CSRF tokens for forms
   - Hash passwords with bcrypt
   - Implement proper access controls

## Common Development Tasks

### Adding a New Model
1. Define the model in `app/models/`
2. Create database migration
3. Update model documentation
4. Add to services layer if needed

### Creating New API Endpoints
1. Add endpoint in `app/api/v1/`
2. Implement proper error handling
3. Add authentication/authorization
4. Update API documentation

### Adding New Services
1. Create service class in `app/services/`
2. Implement business logic
3. Add proper error handling
4. Update service documentation

## Testing and Quality Assurance

### Code Quality
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Document functions and classes
- Implement proper error handling

### Security Review
- Validate all user inputs
- Sanitize data before database operations
- Use parameterized queries
- Implement proper access controls

## Troubleshooting

### Common Issues
- **Database Connection**: Check PostgreSQL service and connection string
- **Migration Errors**: Ensure all migrations are applied in order
- **Email Issues**: Verify SMTP configuration in settings
- **Zoho Integration**: Check credentials and API permissions

### Debug Mode
```bash
# Enable debug mode
export FLASK_ENV=development
export FLASK_DEBUG=1
python run.py
```

### Logging and Monitoring
For comprehensive troubleshooting and system monitoring:

- **[Troubleshooting & Logging Guide](./troubleshooting-logging.md)** - Complete guide to the logging system
- **[Logging Quick Reference](./logging-quick-reference.md)** - Essential commands and shortcuts

**Quick Start for Logging**:
```bash
# Monitor application logs in real-time
tail -f logs/app.log

# Check for errors
grep -i "error" logs/app.log

# Monitor HTTP requests
tail -f logs/access.log

# Check credential access
tail -f logs/credential_access.log
```

## Contributing

When contributing to the codebase:

1. **Follow the existing code style**
2. **Update documentation** for any new features
3. **Test thoroughly** before submitting
4. **Consider security implications** of changes
5. **Update this README** if adding new sections

## Support

For development questions or issues:
- Check the [Architecture Overview](./architecture.md) for system design
- Review [Security Implementation](./security.md) for security guidelines
- Consult the [Models](./models.md) for database structure
- Refer to [Services](./services.md) for business logic patterns

---

**Last Updated**: June 2025  
**Version**: 1.0.0  
**Status**: Production Ready 