# Architecture Overview

## System Architecture

Expiry Tracker follows a modern web application architecture with clear separation of concerns, modular design, and scalable components.

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Templates)   │◄──►│   (Flask App)   │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (PostgreSQL)  │
                       └─────────────────┘
```

### Core Components

1. **Web Interface**: HTML templates with Tailwind CSS
2. **Flask Application**: Python web framework
3. **Database Layer**: PostgreSQL with SQLAlchemy ORM
4. **External Services**: Azure Computer Vision, Gmail SMTP, Zoho CRM
5. **Task Scheduler**: APScheduler for automated tasks

## Application Structure

### Directory Layout

```
app/
├── __init__.py              # Application factory
├── config.py               # Configuration management
├── api/                    # API endpoints
│   └── v1/                # API version 1
├── core/                   # Core functionality
│   ├── extensions.py      # Flask extensions
│   ├── errors.py          # Error handlers
│   └── middleware.py      # Custom middleware
├── models/                 # Database models
├── routes/                 # Web routes
├── services/               # Business logic
├── templates/              # Jinja2 templates
├── static/                 # Static assets
├── forms/                  # WTForms definitions
├── utils/                  # Utility functions
└── tasks/                  # Scheduled tasks
```

### Key Design Patterns

1. **Factory Pattern**: Application factory for configuration
2. **Repository Pattern**: Service layer for data access
3. **Observer Pattern**: Event-driven notifications
4. **Strategy Pattern**: Multiple authentication methods
5. **Template Pattern**: Base classes for common functionality

## Flask Application Structure

### Application Factory

The application uses Flask's application factory pattern:

```python
def create_app(config_name=None):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    init_extensions(app)
    
    # Register blueprints
    register_blueprints(app)
    
    return app
```

### Blueprint Organization

- **Main Blueprint**: Core pages and dashboard
- **Auth Blueprint**: Authentication and user management
- **API Blueprint**: RESTful API endpoints
- **Reports Blueprint**: Report generation and viewing
- **Notifications Blueprint**: Notification management
- **Activities Blueprint**: Activity tracking

### Extension Management

Centralized extension initialization in `core/extensions.py`:

```python
# Core extensions
db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()
migrate = Migrate()
cors = CORS()
scheduler = APScheduler()
mail = Mail()
```

## Database Architecture

### ORM Layer

Uses SQLAlchemy 2.0 with declarative base:

```python
class BaseModel(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Model Relationships

```
User (1) ──── (N) Item
User (1) ──── (N) Report
User (1) ──── (N) Notification
User (1) ──── (N) Activity
Item (1) ──── (N) Notification
```

### Migration Strategy

- **Alembic**: Database migration management
- **Version Control**: All schema changes tracked
- **Rollback Support**: Safe migration rollbacks
- **Data Integrity**: Foreign key constraints

## Service Layer Architecture

### Service Classes

Business logic encapsulated in service classes:

```python
class NotificationService:
    def send_daily_notifications(self, user_id):
        # Business logic for notifications
        
class ReportService:
    def generate_daily_report(self, user_id):
        # Business logic for reports
        
class ZohoService:
    def sync_inventory(self, user):
        # Business logic for Zoho integration
```

### Service Responsibilities

1. **Data Validation**: Input sanitization and validation
2. **Business Logic**: Core application rules
3. **External Integration**: API calls and data transformation
4. **Error Handling**: Graceful error management
5. **Logging**: Activity tracking and debugging

## Security Architecture

### Authentication System

- **Flask-Login**: Session-based authentication
- **JWT**: Token-based authentication for API
- **Password Hashing**: bcrypt for secure storage
- **CSRF Protection**: Cross-site request forgery prevention

### Authorization Model

- **User-Based Access**: Data isolation by user
- **Role-Based Access**: Future extensibility
- **Resource Protection**: Secure endpoint access
- **Session Management**: Secure session handling

### Data Protection

- **Input Validation**: Sanitization of all inputs
- **SQL Injection Prevention**: Parameterized queries
- **XSS Prevention**: Output encoding
- **Encryption**: Sensitive data encryption

## API Architecture

### RESTful Design

- **Resource-Based URLs**: `/api/v1/items/<id>`
- **HTTP Methods**: GET, POST, PUT, DELETE
- **Status Codes**: Proper HTTP response codes
- **JSON Responses**: Consistent response format

### API Versioning

- **URL Versioning**: `/api/v1/` prefix
- **Backward Compatibility**: Maintained across versions
- **Documentation**: Comprehensive API docs
- **Rate Limiting**: Request throttling

### Error Handling

```python
{
    "error": "Validation failed",
    "message": "Detailed error description",
    "details": {
        "field": ["Error message"]
    }
}
```

## External Service Integration

### Azure Computer Vision

- **OCR Processing**: Date extraction from images
- **Error Handling**: Graceful fallback to manual entry
- **Rate Limiting**: API call management
- **Caching**: Result caching for performance

### Gmail SMTP

- **Email Delivery**: Notification system
- **Authentication**: OAuth2 or app passwords
- **Retry Logic**: Failed email handling
- **Template System**: HTML email templates

### Zoho CRM Integration

- **OAuth2 Flow**: Secure authentication
- **Two-Way Sync**: Bidirectional data flow
- **Conflict Resolution**: Data consistency
- **Error Recovery**: Connection failure handling

## Task Scheduling Architecture

### APScheduler Integration

- **Cron Jobs**: Scheduled task execution
- **Job Persistence**: Database-backed job storage
- **Error Handling**: Failed job management
- **Monitoring**: Job execution tracking

### Scheduled Tasks

1. **Daily Notifications**: 9:11 PM BST
2. **Cleanup Tasks**: Expired items and accounts
3. **Report Generation**: Automated daily reports
4. **Data Maintenance**: Database optimization

## Performance Architecture

### Database Optimization

- **Indexing**: Strategic database indexes
- **Query Optimization**: Efficient SQL queries
- **Connection Pooling**: Database connection management
- **Caching**: Result caching strategies

### Application Performance

- **Lazy Loading**: On-demand data loading
- **Pagination**: Large dataset handling
- **Async Processing**: Background task execution
- **Resource Management**: Memory and CPU optimization

## Monitoring and Logging

### Application Logging

- **Structured Logging**: JSON format logs
- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Log Rotation**: File size management
- **Centralized Logging**: Log aggregation

### Error Tracking

- **Exception Handling**: Comprehensive error catching
- **Error Reporting**: Detailed error information
- **Performance Monitoring**: Response time tracking
- **Health Checks**: System status monitoring

## Scalability Considerations

### Horizontal Scaling

- **Stateless Design**: Session-independent architecture
- **Load Balancing**: Multiple server support
- **Database Scaling**: Read replicas and sharding
- **Caching Layer**: Redis integration ready

### Vertical Scaling

- **Resource Optimization**: Memory and CPU efficiency
- **Database Optimization**: Query performance tuning
- **Code Optimization**: Algorithm efficiency
- **Resource Monitoring**: Performance tracking

## Development Workflow

### Code Organization

- **Modular Design**: Clear separation of concerns
- **Dependency Injection**: Loose coupling
- **Configuration Management**: Environment-specific settings
- **Testing Strategy**: Unit and integration tests

### Deployment Architecture

- **Containerization**: Docker deployment
- **Environment Management**: Development, staging, production
- **Configuration Management**: Environment variables
- **Health Monitoring**: Application status tracking

## Future Enhancements

### Planned Features

- **Real-time Notifications**: WebSocket integration
- **Enhanced Reporting**: More detailed reports and insights
- **Mobile App**: Native mobile application
- **Multi-tenant Support**: SaaS architecture

### Technical Improvements

- **Microservices**: Service decomposition
- **Event Sourcing**: Event-driven architecture
- **CQRS**: Command Query Responsibility Segregation
- **GraphQL**: Flexible API querying

---

**Previous**: [Developer Guide Overview](./README.md) | **Next**: [Database Schema](./database.md) 