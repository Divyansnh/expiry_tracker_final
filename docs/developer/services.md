# Services Layer

This document provides a comprehensive overview of the services layer in the Expiry Tracker application.

## Overview

The services layer acts as an intermediary between the API routes and the data models, encapsulating business logic and external integrations. It provides a clean separation of concerns and makes the application more maintainable and testable.

## Service Architecture

### Service Pattern

All services follow a consistent pattern:

```python
class ServiceName:
    def __init__(self):
        # Initialize service dependencies
        pass
    
    def method_name(self, *args, **kwargs):
        # Business logic implementation
        pass
```

### Service Responsibilities

1. **Business Logic**: Encapsulate complex business rules
2. **Data Validation**: Validate input data before processing
3. **External Integrations**: Handle third-party API calls
4. **Error Handling**: Provide consistent error handling
5. **Logging**: Log important operations and errors
6. **Caching**: Implement caching strategies where appropriate

## Core Services

### ActivityService

**Location:** `app/services/activity_service.py`

**Purpose:** Manages user activity tracking and logging.

**Key Methods:**

```python
class ActivityService:
    def log_item_added(self, user_id: int, item_name: str, item_id: int) -> None:
        """Log when a new item is added to inventory."""
        
    def log_item_updated(self, user_id: int, item_name: str, item_id: int, changes: dict) -> None:
        """Log when an item is updated with change details."""
        
    def log_item_deleted(self, user_id: int, item_name: str, item_id: int) -> None:
        """Log when an item is deleted from inventory."""
        
    def get_user_activities(self, user_id: int, limit: int = 20) -> List[Dict]:
        """Get recent activities for a user."""
        
    def get_activities_paginated(self, user_id: int, page: int = 1, per_page: int = 20,
                                activity_type: str = 'all') -> tuple[List[Dict], int]:
        """Get paginated activities with filtering."""
        
    def get_recent_activities_for_dashboard(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Get recent activities formatted for dashboard display."""
```

**Usage Example:**
```python
# In API route
activity_service = ActivityService()
activity_service.log_item_added(current_user.id, "Milk", item.id)

# Get activities for display
activities, total = activity_service.get_activities_paginated(
    current_user.id, 
    page=1, 
    per_page=20,
    activity_type='item_added'
)
```

### DateOCRService

**Location:** `app/services/date_ocr_service.py`

**Purpose:** Handles date extraction from images using Azure Computer Vision.

**Key Methods:**

```python
class DateOCRService:
    def __init__(self):
        """Initialize Azure Computer Vision client."""
        
    def extract_date_from_image(self, image_data: bytes) -> Dict[str, Any]:
        """Extract expiry date from image using OCR."""
        
    def _parse_date_text(self, text: str) -> Optional[str]:
        """Parse date text and return in YYYY-MM-DD format."""
        
    def _validate_date(self, date_str: str) -> bool:
        """Validate extracted date format and logic."""
```

**Usage Example:**
```python
# In API route
ocr_service = DateOCRService()
result = ocr_service.extract_date_from_image(image_file.read())

if result['status'] == 'success':
    expiry_date = result['date']
else:
    error_message = result['error']
```

### EmailService

**Location:** `app/services/email_service.py`

**Purpose:** Handles email sending and template rendering.

**Key Methods:**

```python
class EmailService:
    def __init__(self):
        """Initialize email configuration."""
        
    def send_email(self, to_email: str, subject: str, template: str, 
                   context: dict = None) -> bool:
        """Send email using specified template."""
        
    def send_password_reset_email(self, user: User, reset_url: str) -> bool:
        """Send password reset email."""
        
    def send_email_verification(self, user: User, verification_url: str) -> bool:
        """Send email verification."""
        
    def send_daily_notification(self, user: User, items: List[Item]) -> bool:
        """Send daily expiry notification."""
        
    def send_test_notification(self, user: User) -> bool:
        """Send test notification email."""
```

**Usage Example:**
```python
# In notification service
email_service = EmailService()
success = email_service.send_daily_notification(user, expiring_items)

if not success:
    logger.error(f"Failed to send notification to {user.email}")
```

### NotificationService

**Location:** `app/services/notification_service.py`

**Purpose:** Manages notification creation, delivery, and preferences.

**Key Methods:**

```python
class NotificationService:
    def create_notification(self, user_id: int, message: str, 
                           notification_type: str = 'email', 
                           item_id: int = None) -> Notification:
        """Create a new notification."""
        
    def get_user_notifications(self, user_id: int, limit: int = 20) -> List[Notification]:
        """Get recent notifications for a user."""
        
    def get_notifications_paginated(self, user_id: int, page: int = 1, 
                                   per_page: int = 20, filter_type: str = 'all',
                                   search: str = None) -> tuple[List[Dict], int]:
        """Get paginated notifications with filtering."""
        
    def mark_notification_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark a specific notification as read."""
        
    def mark_all_notifications_as_read(self, user_id: int) -> bool:
        """Mark all pending notifications as read."""
        
    def send_expiry_notifications(self) -> None:
        """Send notifications for items expiring soon."""
        
    def get_notification_stats(self, user_id: int) -> Dict[str, int]:
        """Get notification statistics for a user."""
```

**Usage Example:**
```python
# In API route
notification_service = NotificationService()
notifications, total = notification_service.get_notifications_paginated(
    current_user.id,
    page=1,
    per_page=20,
    filter_type='pending'
)

# Mark as read
notification_service.mark_notification_as_read(notification_id, current_user.id)
```

### ReportService

**Location:** `app/services/report_service.py`

**Purpose:** Generates and manages inventory reports.

**Key Methods:**

```python
class ReportService:
    def generate_daily_report(self, user_id: int, report_date: date = None) -> Report:
        """Generate daily inventory report."""
        
    def get_user_reports(self, user_id: int, limit: int = 20) -> List[Report]:
        """Get recent reports for a user."""
        
    def get_reports_paginated(self, user_id: int, page: int = 1, 
                             per_page: int = 20, start_date: str = None,
                             end_date: str = None) -> tuple[List[Dict], int]:
        """Get paginated reports with date filtering."""
        
    def get_report_by_id(self, report_id: int, user_id: int) -> Optional[Report]:
        """Get specific report by ID."""
        
    def delete_report(self, report_id: int, user_id: int) -> bool:
        """Delete a report."""
        
    def get_historical_comparison(self, user_id: int, current_report: Report) -> Dict:
        """Compare current report with historical data."""
```

**Usage Example:**
```python
# In API route
report_service = ReportService()
report = report_service.generate_daily_report(current_user.id)

# Get reports with filtering
reports, total = report_service.get_reports_paginated(
    current_user.id,
    page=1,
    per_page=20,
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

### ZohoService

**Location:** `app/services/zoho_service.py`

**Purpose:** Handles integration with Zoho CRM for inventory synchronization.

**Key Methods:**

```python
class ZohoService:
    def __init__(self, user: User):
        """Initialize with user's Zoho credentials."""
        
    def authenticate(self, client_id: str, client_secret: str, 
                    authorization_code: str) -> bool:
        """Authenticate with Zoho using authorization code."""
        
    def refresh_access_token(self) -> bool:
        """Refresh expired access token."""
        
    def get_organizations(self) -> List[Dict]:
        """Get user's Zoho organizations."""
        
    def create_item_in_zoho(self, item_data: Dict) -> Optional[Dict]:
        """Create item in Zoho CRM."""
        
    def update_item_in_zoho(self, zoho_item_id: str, item_data: Dict) -> bool:
        """Update item in Zoho CRM."""
        
    def delete_item_in_zoho(self, zoho_item_id: str) -> bool:
        """Delete item from Zoho CRM."""
        
    def sync_items_to_zoho(self, items: List[Item]) -> Dict[str, int]:
        """Sync multiple items to Zoho CRM."""
        
    def disconnect_zoho(self) -> bool:
        """Disconnect Zoho integration."""
```

**Usage Example:**
```python
# In API route
zoho_service = ZohoService(current_user)

# Create item in Zoho
zoho_item = zoho_service.create_item_in_zoho(item_data)
if zoho_item:
    item.zoho_item_id = zoho_item['item_id']

# Sync items
sync_results = zoho_service.sync_items_to_zoho(user_items)
print(f"Synced {sync_results['success']} items, {sync_results['failed']} failed")
```

## Service Dependencies

### Database Access

Services use SQLAlchemy models for database operations:

```python
from app.models.item import Item
from app.models.user import User
from app.models.activity import Activity
from app.core.extensions import db
```

### External Dependencies

```python
# Azure Computer Vision
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

# Email
from flask_mail import Mail, Message

# Logging
import logging
logger = logging.getLogger(__name__)
```

## Error Handling

### Service-Level Error Handling

```python
class ServiceError(Exception):
    """Base exception for service errors."""
    pass

class ValidationError(ServiceError):
    """Raised when input validation fails."""
    pass

class ExternalServiceError(ServiceError):
    """Raised when external service calls fail."""
    pass

# In service methods
try:
    # Service logic
    result = self._process_data(data)
    return result
except ValidationError as e:
    logger.error(f"Validation error: {e}")
    raise
except ExternalServiceError as e:
    logger.error(f"External service error: {e}")
    raise
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise ServiceError(f"Service operation failed: {str(e)}")
```

### Consistent Error Responses

```python
def handle_service_error(error: Exception) -> Dict[str, Any]:
    """Convert service errors to consistent API responses."""
    if isinstance(error, ValidationError):
        return {'error': 'Validation failed', 'details': str(error)}
    elif isinstance(error, ExternalServiceError):
        return {'error': 'External service unavailable', 'message': str(error)}
    else:
        return {'error': 'Internal server error', 'message': str(error)}
```

## Logging and Monitoring

### Service Logging

```python
import logging

logger = logging.getLogger(__name__)

class ActivityService:
    def log_item_added(self, user_id: int, item_name: str, item_id: int) -> None:
        logger.info(f"User {user_id} added item '{item_name}' (ID: {item_id})")
        # Implementation...
        
    def get_activities_paginated(self, user_id: int, page: int = 1, 
                                per_page: int = 20, activity_type: str = 'all') -> tuple[List[Dict], int]:
        logger.debug(f"Fetching activities for user {user_id}, page {page}, type {activity_type}")
        # Implementation...
```

### Performance Monitoring

```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator to monitor service method performance."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    return wrapper

# Usage
@monitor_performance
def generate_daily_report(self, user_id: int, report_date: date = None) -> Report:
    # Implementation...
```

## Best Practices

### Service Design Principles

1. **Single Responsibility**: Each service has one clear purpose
2. **Dependency Injection**: Services accept dependencies as parameters
3. **Error Handling**: Consistent error handling across all services
4. **Logging**: Comprehensive logging for debugging and monitoring

### Performance Considerations

1. **Database Queries**: Optimize queries and use appropriate indexes
2. **Caching**: Cache frequently accessed data
3. **Async Operations**: Use async for external API calls where possible
4. **Batch Operations**: Process multiple items in batches
5. **Connection Pooling**: Reuse database connections

### Security Considerations

1. **Input Validation**: Validate all input data
2. **SQL Injection**: Use parameterized queries
3. **Authentication**: Verify user permissions before operations
4. **Data Encryption**: Encrypt sensitive data
5. **Audit Logging**: Log all sensitive operations

---

**Previous**: [Database Schema](./database.md) | **Next**: [Models](./models.md) 