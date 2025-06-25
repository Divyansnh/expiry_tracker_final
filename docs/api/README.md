# API Documentation

## Overview

The Expiry Tracker API provides a comprehensive RESTful interface for managing inventory, reports, notifications, and user settings. All endpoints are secured with authentication and CSRF protection.

**Note:** This documentation covers both API endpoints (returning JSON responses) and web routes (handling form submissions and redirects). API endpoints are implemented in `app/api/v1/` while web routes are implemented in `app/routes/`.

## Base URL

```
Development: http://localhost:5000/api/v1
Production: https://your-domain.com/api/v1
```

## Authentication

### Session-Based Authentication

The API uses Flask-Login for session-based authentication. Users must be logged in to access protected endpoints.

**Headers Required:**
```
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

### CSRF Protection

All POST, PUT, DELETE requests require a valid CSRF token:

1. **Get CSRF Token:**
   ```html
   <meta name="csrf-token" content="{{ csrf_token() }}">
   ```

2. **Include in Requests:**
   ```javascript
   headers: {
       'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content,
       'Content-Type': 'application/json'
   }
   ```

## Response Format

### Success Response
```json
{
    "message": "Operation completed successfully",
    "data": {
        // Response data
    }
}
```

### Error Response
```json
{
    "error": "Error description",
    "message": "Detailed error message"
}
```

### Pagination Response
```json
{
    "items": [...],
    "pagination": {
        "current_page": 1,
        "per_page": 20,
        "total_count": 100,
        "total_pages": 5,
        "has_next": true,
        "has_prev": false
    }
}
```

## HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 429 | Too Many Requests |
| 500 | Internal Server Error |

## Rate Limiting

- **General Endpoints**: 100 requests per minute
- **Authentication Endpoints**: 5 requests per minute
- **File Upload Endpoints**: 10 requests per minute

## API Endpoints

### Inventory Management
- `POST /items` - Create new item or update existing
- `GET /items/<id>` - Get specific item
- `PUT /items/<id>` - Update item
- `DELETE /items/<id>` - Delete item
- `POST /items/bulk-delete` - Bulk delete items
- `GET /items/filter` - Filter and search items
- `POST /items/check` - Check item existence

### Reports
- `GET /reports` - List reports
- `POST /reports/generate` - Generate new report
- `GET /reports/<id>` - Get specific report
- `DELETE /reports/<id>` - Delete report

### Notifications
- `GET /notifications` - List notifications
- `PUT /notifications/read-all` - Mark all as read
- `PUT /notifications/<id>/read` - Mark specific notification as read
- `GET /notifications/preferences` - Get preferences
- `PUT /notifications/preferences` - Update preferences
- `POST /notifications/test` - Send test notification

### Settings
- `PUT /settings/notifications` - Update notification settings
- `PUT /settings/zoho-credentials` - Update Zoho credentials
- `DELETE /settings/disconnect-zoho` - Disconnect Zoho
- `POST /settings/verify-password-for-*` - Password verification endpoints

### Date OCR
- `POST /date_ocr/extract` - Extract date from image

## Web Routes

### Authentication & Users
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/forgot-password` - Password reset request
- `POST /auth/reset_password/<token>` - Password reset

### Activities
- `GET /api/v1/activities` - List user activities (implemented in routes layer)

## Error Handling

### Validation Errors
```json
{
    "error": "Validation failed",
    "details": {
        "field_name": ["Error message"]
    }
}
```

### Authentication Errors
```json
{
    "error": "Authentication required",
    "message": "Please log in to access this resource"
}
```

### Rate Limit Errors
```json
{
    "error": "Rate limit exceeded",
    "message": "Too many requests. Please try again later.",
    "retry_after": 60
}
```

## Examples

### JavaScript (Fetch API)

```javascript
// Get items with filtering
async function getItems(filters = {}) {
    const params = new URLSearchParams(filters);
    const response = await fetch(`/api/v1/items/filter?${params}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch items');
    }
    
    return response.json();
}

// Create new item
async function createItem(itemData) {
    const response = await fetch('/api/v1/items', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(itemData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to create item');
    }
    
    return response.json();
}

// Update item
async function updateItem(itemId, itemData) {
    const response = await fetch(`/api/v1/items/${itemId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        },
        body: JSON.stringify(itemData)
    });
    
    if (!response.ok) {
        throw new Error('Failed to update item');
    }
    
    return response.json();
}

// Delete item
async function deleteItem(itemId) {
    const response = await fetch(`/api/v1/items/${itemId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to delete item');
    }
    
    return response.json();
}

// Get notifications
async function getNotifications(page = 1, filter = 'all') {
    const response = await fetch(`/api/v1/notifications?page=${page}&filter=${filter}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch notifications');
    }
    
    return response.json();
}

// Mark all notifications as read
async function markAllNotificationsAsRead() {
    const response = await fetch('/api/v1/notifications/read-all', {
        method: 'PUT',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to mark notifications as read');
    }
    
    return response.json();
}

// Get activities
async function getActivities(page = 1, type = 'all') {
    const response = await fetch(`/api/v1/activities?page=${page}&type=${type}`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
        }
    });
    
    if (!response.ok) {
        throw new Error('Failed to fetch activities');
    }
    
    return response.json();
}

// Extract date from image
async function extractDateFromImage(imageFile) {
    const formData = new FormData();
    formData.append('image', imageFile);
    
    const response = await fetch('/api/v1/date_ocr/extract', {
        method: 'POST',
        body: formData
    });
    
    if (!response.ok) {
        throw new Error('Failed to extract date');
    }
    
    return response.json();
}
```

### Python

```python
import requests

def get_items(session, filters=None):
    response = session.get('/api/v1/items/filter', params=filters or {})
    return response.json()

def create_item(session, item_data):
    response = session.post('/api/v1/items', json=item_data)
    return response.json()

def update_item(session, item_id, item_data):
    response = session.put(f'/api/v1/items/{item_id}', json=item_data)
    return response.json()

def delete_item(session, item_id):
    response = session.delete(f'/api/v1/items/{item_id}')
    return response.json()

def get_notifications(session, page=1, filter='all'):
    response = session.get('/api/v1/notifications', params={'page': page, 'filter': filter})
    return response.json()

def mark_all_notifications_read(session):
    response = session.put('/api/v1/notifications/read-all')
    return response.json()

def get_activities(session, page=1, type='all'):
    response = session.get('/api/v1/activities', params={'page': page, 'type': type})
    return response.json()

def extract_date_from_image(session, image_path):
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = session.post('/api/v1/date_ocr/extract', files=files)
    return response.json()
```

## Best Practices

1. **Always validate input data** before sending to API
2. **Handle pagination** for large datasets
3. **Use appropriate status codes** in your application
4. **Implement proper error handling** for all API calls
5. **Cache frequently accessed data** to improve performance
6. **Use bulk operations** when dealing with multiple items
7. **Monitor API rate limits** and implement backoff strategies

## Rate Limits

- **GET requests**: 100 per minute
- **POST/PUT/DELETE requests**: 50 per minute
- **Bulk operations**: 10 per minute

---

**Last Updated**: December 2024  
**API Version**: v1 