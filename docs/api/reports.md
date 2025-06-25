# Reports API

This document covers the Reports API endpoints for generating and managing inventory reports.

## Overview

The Reports API provides endpoints for generating daily inventory reports, retrieving report history, and managing report data. All endpoints require authentication.

## Authentication

All endpoints require a valid session cookie. Include the CSRF token in request headers for POST/DELETE requests.

**Headers:**
```
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

## Endpoints

### Get Reports

**GET** `/api/v1/reports`

Retrieve user's reports with optional date filtering and pagination.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)
- `start_date` (optional): Start date filter (YYYY-MM-DD)
- `end_date` (optional): End date filter (YYYY-MM-DD)

**Response:**
```json
{
  "reports": [
    {
      "id": 1,
      "date": "2024-12-20",
      "total_items": 150,
      "expiring_items": 12,
      "expired_items": 3,
      "low_stock_items": 8,
      "total_value": 2500.50,
      "created_at": "2024-12-20T15:30:00Z"
    }
  ],
  "pagination": {
    "current_page": 1,
    "per_page": 20,
    "total_count": 50,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### Generate Report

**POST** `/api/v1/reports/generate`

Generate a new daily inventory report for the current user.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "message": "Report generated successfully",
  "report": {
    "id": 2,
    "date": "2024-12-21",
    "total_items": 155,
    "expiring_items": 15,
    "expired_items": 2,
    "low_stock_items": 10,
    "total_value": 2600.75,
    "created_at": "2024-12-21T10:00:00Z"
  }
}
```

### Get Specific Report

**GET** `/api/v1/reports/{report_id}`

Retrieve a specific report by ID.

**Response:**
```json
{
  "report": {
    "id": 1,
    "date": "2024-12-20",
    "total_items": 150,
    "expiring_items": 12,
    "expired_items": 3,
    "low_stock_items": 8,
    "total_value": 2500.50,
    "created_at": "2024-12-20T15:30:00Z",
    "report_data": {
      "comprehensive_expiry_analysis": {
        "overall_metrics": {
          "expired_percentage": 2.0,
          "expiring_soon_percentage": 8.0,
          "short_term_percentage": 15.0,
          "medium_term_percentage": 25.0
        }
      },
      "historical_comparison": {
        "last_week": {
          "total_items": 145,
          "expiring_items": 10,
          "expired_items": 2,
          "low_stock_items": 6,
          "total_value": 2400.00,
          "value_at_risk": 5.2
        }
      }
    }
  }
}
```

### Delete Report

**DELETE** `/api/v1/reports/{report_id}`

Delete a specific report (requires enhanced security verification).

**Response:**
```json
{
  "message": "Report deleted successfully"
}
```

## Report Data Structure

### Basic Report

```json
{
  "id": 1,
  "date": "2024-12-20",
  "total_items": 150,
  "expiring_items": 12,
  "expired_items": 3,
  "low_stock_items": 8,
  "total_value": 2500.50,
  "created_at": "2024-12-20T15:30:00Z"
}
```

### Detailed Report with Analysis

```json
{
  "id": 1,
  "date": "2024-12-20",
  "total_items": 150,
  "expiring_items": 12,
  "expired_items": 3,
  "low_stock_items": 8,
  "total_value": 2500.50,
  "created_at": "2024-12-20T15:30:00Z",
  "report_data": {
    "comprehensive_expiry_analysis": {
      "overall_metrics": {
        "expired_percentage": 2.0,
        "expiring_soon_percentage": 8.0,
        "short_term_percentage": 15.0,
        "medium_term_percentage": 25.0
      },
      "expired_items": [
        {
          "name": "Product A",
          "quantity": 5,
          "expiry_date": "2024-12-18",
          "days_overdue": 2,
          "value": 50.00,
          "location": "Warehouse A",
          "batch_number": "B001"
        }
      ],
      "expiring_soon_items": [
        {
          "name": "Product B",
          "quantity": 10,
          "expiry_date": "2024-12-25",
          "days_until_expiry": 5,
          "value": 100.00,
          "location": "Warehouse B",
          "batch_number": "B002"
        }
      ]
    },
    "historical_comparison": {
      "last_week": {
        "total_items": 145,
        "expiring_items": 10,
        "expired_items": 2,
        "low_stock_items": 6,
        "total_value": 2400.00,
        "value_at_risk": 5.2
      }
    }
  }
}
```

## Error Responses

### Report Not Found

```http
HTTP/1.1 404 Not Found
Content-Type: application/json

{
  "error": "Report not found"
}
```

### Generation Failed

```http
HTTP/1.1 500 Internal Server Error
Content-Type: application/json

{
  "error": "Failed to generate report"
}
```

### Invalid Date Range

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Start date cannot be after end date"
}
```

## Usage Examples

### Get All Reports

```javascript
fetch('/api/v1/reports')
.then(response => response.json())
.then(data => {
  console.log('Reports:', data.reports);
  console.log('Pagination:', data.pagination);
});
```

### Get Reports with Date Filter

```javascript
const params = new URLSearchParams({
  start_date: '2024-12-01',
  end_date: '2024-12-31',
  page: 1,
  per_page: 10
});

fetch(`/api/v1/reports?${params}`)
.then(response => response.json())
.then(data => {
  console.log('Filtered reports:', data.reports);
});
```

### Generate New Report

```javascript
fetch('/api/v1/reports/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({})
})
.then(response => response.json())
.then(data => {
  console.log('Report generated:', data.message);
  console.log('New report:', data.report);
});
```

### Get Specific Report

```javascript
fetch('/api/v1/reports/123')
.then(response => response.json())
.then(data => {
  console.log('Report details:', data.report);
  console.log('Expiry analysis:', data.report.report_data.comprehensive_expiry_analysis);
});
```

### Delete Report

```javascript
fetch('/api/v1/reports/123', {
  method: 'DELETE',
  headers: {
    'X-CSRFToken': csrfToken
  }
})
.then(response => response.json())
.then(data => {
  console.log('Report deleted:', data.message);
});
```

## Report Features

### Historical Comparison

Reports include comparison with data from 7 days ago:
- Total items count
- Expiring items count
- Expired items count
- Low stock items count
- Total value
- Value at risk percentage

### Expiry Analysis

Comprehensive analysis of items by expiry status:
- **Expired**: Items past expiry date
- **Critical**: Items expiring within 7 days
- **Short-term**: Items expiring within 8-30 days
- **Medium-term**: Items expiring within 31-90 days

### Risk Assessment

Each item includes:
- Risk score based on expiry proximity
- Value at risk calculations
- Location and batch tracking

---

**Previous**: [Notifications API](./notifications.md) | **Next**: [Settings API](./settings.md) 