# Notifications API

This document covers the Notifications API endpoints for managing email notifications.

## Overview

The Notifications API provides endpoints for viewing notification history, marking notifications as read, and managing notification preferences.

## Authentication

All endpoints require a valid session cookie. Include the CSRF token in request headers for POST/PUT/DELETE requests.

**Headers:**
```
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

## Endpoints

### Get Notifications

**GET** `/api/v1/notifications`

Retrieve paginated list of notifications.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `filter` (optional): Filter type - 'all', 'sent', 'pending' (default: 'all')
- `search` (optional): Search term for notification message
- `search_mode` (optional): Search mode - 'message' (default: 'message')

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 1,
      "item_id": 1,
      "message": "You have 5 items expiring within 7 days",
      "type": "email",
      "status": "pending",
      "priority": "normal",
      "created_at": "2024-12-20T15:45:00Z",
      "sent_at": null
    }
  ],
  "stats": {
    "total_sent": 25,
    "total_pending": 5,
    "total_all": 30
  },
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_count": 30,
    "total_pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

### Mark Notification as Read

**PUT** `/api/v1/notifications/{notification_id}/read`

Mark a specific notification as read.

**Response:**
```json
{
  "message": "Notification marked as read"
}
```

### Mark All Notifications as Read

**PUT** `/api/v1/notifications/read-all`

Mark all pending notifications as read.

**Response:**
```json
{
  "message": "All notifications marked as read"
}
```

### Get Notification Preferences

**GET** `/api/v1/notifications/preferences`

Retrieve current notification preferences.

**Response:**
```json
{
  "email_notifications": true
}
```

### Update Notification Preferences

**PUT** `/api/v1/notifications/preferences`

Update notification preferences.

**Request Body:**
```json
{
  "email_notifications": true
}
```

**Response:**
```json
{
  "message": "Notification preferences updated"
}
```

### Test Notifications

**POST** `/api/v1/notifications/test`

Send a test notification.

**Request Body:**
```json
{
  "type": "email"
}
```

**Response:**
```json
{
  "message": "Test notification sent successfully"
}
```

## Notification Data Structure

### Notification Object

```json
{
  "id": 1,
  "user_id": 1,
  "item_id": 1,
  "message": "You have 5 items expiring within 7 days",
  "type": "email",
  "status": "pending",
  "priority": "normal",
  "created_at": "2024-12-20T15:45:00Z",
  "sent_at": null
}
```

### Notification Stats

```json
{
  "total_sent": 25,
  "total_pending": 5,
  "total_all": 30
}
```

### Pagination Info

```json
{
  "current_page": 1,
  "per_page": 20,
  "total_count": 30,
  "total_pages": 2,
  "has_next": true,
  "has_prev": false
}
```

## Error Responses

### Notification Not Found

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "Notification not found"
}
```

### Server Error

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Error message"
}
```

## Usage Examples

### Get Notifications

```javascript
fetch('/api/v1/notifications?page=1&per_page=20&filter=all')
.then(response => response.json())
.then(data => {
  console.log('Notifications:', data.notifications);
  console.log('Stats:', data.stats);
  console.log('Pagination:', data.pagination);
});
```

### Mark Notification as Read

```javascript
fetch('/api/v1/notifications/123/read', {
  method: 'PUT',
  headers: {
    'X-CSRFToken': csrfToken
  }
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data.message);
});
```

### Mark All Notifications as Read

```javascript
fetch('/api/v1/notifications/read-all', {
  method: 'PUT',
  headers: {
    'X-CSRFToken': csrfToken
  }
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data.message);
});
```

### Get Notification Preferences

```javascript
fetch('/api/v1/notifications/preferences')
.then(response => response.json())
.then(data => {
  console.log('Email notifications enabled:', data.email_notifications);
});
```

### Update Notification Preferences

```javascript
fetch('/api/v1/notifications/preferences', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    email_notifications: true
  })
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data.message);
});
```

### Send Test Notification

```javascript
fetch('/api/v1/notifications/test', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    type: 'email'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Result:', data.message);
});
```

## Frontend Features

The notifications page includes:

- **Notification List**: Display of all notifications with status indicators
- **Filter Options**: Filter by status (all, sent, pending)
- **Search Functionality**: Search through notification messages
- **Pagination**: Navigate through large notification lists
- **Bulk Actions**: Mark all notifications as read
- **Individual Actions**: Mark specific notifications as read
- **Statistics**: Display of notification counts by status
- **Test Notifications**: Send test notifications to verify email setup

---

**Previous**: [Items API](./items.md) | **Next**: [Reports API](./reports.md) 