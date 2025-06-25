# Activities API

This document covers the Activities API endpoint for tracking user actions and system events.

## Overview

The Activities API provides a single endpoint for viewing user activity logs with pagination and activity type filtering. This endpoint is implemented in the routes layer but functions as an API endpoint, returning JSON responses.

## Authentication

All endpoints require a valid session cookie.

## Endpoints

### Get Activities

**GET** `/api/v1/activities`

Retrieve paginated list of user activities.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `type` (optional): Filter by activity type (default: 'all')

**Response:**
```json
{
  "activities": [
    {
      "id": 1,
      "user_id": 1,
      "activity_type": "item_added",
      "title": "New item added",
      "description": "Product \"Milk\" was added to inventory",
      "activity_data": {
        "item_id": 1,
        "item_name": "Milk"
      },
      "created_at": "2024-12-20T15:30:00Z",
      "time_ago": "2 hours ago",
      "icon": "fas fa-plus",
      "color": "green"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "pages": 3
}
```

## Activity Types

The following activity types are supported:

- **`item_added`**: New item created
- **`item_updated`**: Item information modified
- **`item_deleted`**: Item removed from inventory
- **`expiry_alert`**: Expiry alert triggered
- **`notification_sent`**: Email notification delivered
- **`report_generated`**: Report created
- **`settings_updated`**: Settings modified
- **`zoho_sync`**: Zoho synchronization
- **`login`**: User logged in
- **`logout`**: User logged out

## Activity Data Structure

### Activity Object

```json
{
  "id": 1,
  "user_id": 1,
  "activity_type": "item_added",
  "title": "New item added",
  "description": "Product \"Milk\" was added to inventory",
  "activity_data": {
    "item_id": 1,
    "item_name": "Milk"
  },
  "created_at": "2024-12-20T15:30:00Z",
  "time_ago": "2 hours ago",
  "icon": "fas fa-plus",
  "color": "green"
}
```

## Error Responses

### Server Error

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Error message"
}
```

## Usage Examples

### Get All Activities

```javascript
fetch('/api/v1/activities')
.then(response => response.json())
.then(data => {
  console.log('Activities:', data.activities);
  console.log('Total:', data.total);
  console.log('Pages:', data.pages);
});
```

### Get Activities with Pagination

```javascript
fetch('/api/v1/activities?page=2&per_page=10')
.then(response => response.json())
.then(data => {
  console.log('Page 2 activities:', data.activities);
});
```

### Filter by Activity Type

```javascript
fetch('/api/v1/activities?type=item_added')
.then(response => response.json())
.then(data => {
  console.log('Item added activities:', data.activities);
});
```

### Frontend Implementation Example

```javascript
function loadActivities() {
  const params = new URLSearchParams({
    page: currentPage,
    per_page: currentPerPage,
    type: currentType
  });
  
  fetch(`/api/v1/activities?${params}`)
    .then(response => response.json())
    .then(data => {
      if (data.error) {
        showError(data.error);
        return;
      }
      
      displayActivities(data.activities);
      updatePagination(data);
    })
    .catch(error => {
      console.error('Error loading activities:', error);
      showError('Failed to load activities');
    });
}
```

## Frontend Features

The activities page includes:

- **Activity Type Filter**: Dropdown to filter by activity type
- **Items per Page**: Selector for pagination size (10, 20, 50, 100)
- **Pagination**: Previous/Next navigation with page info
- **Activity Display**: Each activity shows:
  - Icon and color based on activity type
  - Title and description
  - Time ago (human-readable)
  - Activity type label
- **Loading States**: Loading spinner and empty state
- **Error Handling**: Error display for failed requests

## Implementation Note

This endpoint is implemented in the routes layer (`app/routes/activities.py`) but functions as an API endpoint, returning JSON responses. It follows the same authentication and response patterns as other API endpoints.

---

**Previous**: [Settings API](./settings.md) | **Next**: [Authentication Routes](./authentication.md) 