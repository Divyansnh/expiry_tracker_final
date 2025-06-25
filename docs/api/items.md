# Items API

This document covers the Items API endpoints for managing inventory items.

## Overview

The Items API provides comprehensive endpoints for managing inventory items, including CRUD operations, filtering, search, and bulk operations.

## Authentication

All endpoints require a valid session cookie. Include the CSRF token in request headers for POST/PUT/DELETE requests.

**Headers:**
```
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

## Endpoints

### Create New Item

**POST** `/api/v1/items`

Create a new inventory item or update existing item if name matches.

**Request Body:**
```json
{
    "name": "Product Name",
    "description": "Product description",
    "quantity": 100.0,
    "unit": "pieces",
    "selling_price": 15.00,
    "cost_price": 12.00,
    "expiry_date": "2024-12-31"
}
```

**Required Fields:**
- `name` (string): Item name
- `quantity` (float): Current quantity
- `unit` (string): Unit of measurement
- `selling_price` (float): Selling price
- `expiry_date` (string): Expiry date (YYYY-MM-DD)

**Response:**
```json
{
    "message": "Item created successfully",
    "item": {
        "id": 1,
        "name": "Product Name",
        "description": "Product description",
        "quantity": 100.0,
        "unit": "pieces",
        "selling_price": 15.00,
        "cost_price": 12.00,
        "expiry_date": "2024-12-31T00:00:00",
        "status": "active",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "days_until_expiry": 45
    }
}
```

### Check Item Existence

**POST** `/api/v1/items/check`

Check if an item with the given name already exists.

**Request Body:**
```json
{
    "name": "Product Name"
}
```

**Response:**
```json
{
    "exists": true,
    "item": {
        "id": 1,
        "name": "Product Name",
        "quantity": 100.0,
        "status": "active"
    }
}
```

### Get Specific Item

**GET** `/api/v1/items/{id}`

Retrieve a specific item by ID.

**Path Parameters:**
- `id` (integer): Item ID

**Response:**
```json
{
    "item": {
        "id": 1,
        "name": "Product Name",
        "description": "Product description",
        "quantity": 100.0,
        "unit": "pieces",
        "selling_price": 15.00,
        "cost_price": 12.00,
        "expiry_date": "2024-12-31T00:00:00",
        "status": "active",
        "created_at": "2024-01-15T10:30:00",
        "updated_at": "2024-01-15T10:30:00",
        "days_until_expiry": 45
    }
}
```

### Update Item

**PUT** `/api/v1/items/{id}`

Update an existing item.

**Path Parameters:**
- `id` (integer): Item ID

**Request Body:**
```json
{
    "name": "Updated Product Name",
    "quantity": 150.0,
    "expiry_date": "2025-01-31",
    "selling_price": 18.00
}
```

**Response:**
```json
{
    "message": "Item updated successfully",
    "item": {
        "id": 1,
        "name": "Updated Product Name",
        "quantity": 150.0,
        "expiry_date": "2025-01-31T00:00:00",
        "selling_price": 18.00,
        "status": "active",
        "updated_at": "2024-01-15T11:00:00",
        "days_until_expiry": 380
    }
}
```

### Delete Item

**DELETE** `/api/v1/items/{id}`

Delete an item.

**Path Parameters:**
- `id` (integer): Item ID

**Response:**
```json
{
    "message": "Item deleted successfully"
}
```

### Bulk Delete Items

**POST** `/api/v1/items/bulk-delete`

Delete multiple items at once.

**Request Body:**
```json
{
    "item_ids": [1, 2, 3, 4, 5]
}
```

**Response:**
```json
{
    "message": "Successfully deleted 5 items"
}
```

### Filter and Search Items

**GET** `/api/v1/items/filter`

Advanced filtering and search for items.

**Query Parameters:**
- `search` (string, optional): Search term for name/description
- `status` (string, optional): Filter by status (active, expired, expiring_soon, pending)
- `price_range` (string, optional): Price range filter (cost_under_50, cost_50_100, cost_over_100, selling_under_50, selling_50_100, selling_over_100)
- `quantity_status` (string, optional): Quantity status (low_stock, out_of_stock, well_stocked)
- `date_range` (string, optional): Date range filter (7_days, 30_days, 90_days, no_expiry)
- `sort_by` (string, optional): Sort field (name, quantity, cost_price, selling_price, status, expiry_date)
- `sort_order` (string, optional): Sort order (asc, desc)

**Example Request:**
```
GET /api/v1/items/filter?search=milk&status=expiring_soon&price_range=cost_under_50&sort_by=expiry_date&sort_order=asc
```

**Response:**
```json
[
    {
        "id": 1,
        "name": "Organic Milk",
        "description": "Fresh organic milk",
        "quantity": 50.0,
        "unit": "liters",
        "expiry_date": "2024-02-15T00:00:00",
        "cost_price": 2.50,
        "selling_price": 3.50,
        "status": "expiring_soon",
        "days_until_expiry": 15
    }
]
```

## Item Status Values

| Status | Description |
|--------|-------------|
| `active` | Item is active and not expiring soon |
| `expired` | Item has passed its expiry date |
| `expiring_soon` | Item expires within 30 days |
| `pending` | Item has no expiry date set |

## Validation Rules

### Name
- Required
- Maximum 100 characters
- Must be unique per user

### Quantity
- Required
- Must be a positive number
- Maximum 999999.99

### Unit
- Required
- Maximum 20 characters
- Common values: pieces, kg, liters, boxes, etc.

### Expiry Date
- Required
- Must be a valid date
- Must be in YYYY-MM-DD format
- Cannot be in the past (for new items)

### Prices
- `selling_price` is required
- `cost_price` is optional
- Must be positive numbers
- Maximum 999999.99

## Error Responses

### Validation Error
```json
{
    "error": "Validation failed",
    "details": {
        "name": ["Name is required"],
        "quantity": ["Quantity must be a positive number"],
        "expiry_date": ["Invalid date format"]
    }
}
```

### Item Not Found
```json
{
    "error": "Item not found"
}
```

### Duplicate Item
```json
{
    "error": "Item already exists",
    "message": "An item with this name already exists"
}
```

## Usage Examples

### Create New Item

```javascript
const itemData = {
    name: "Organic Milk",
    description: "Fresh organic milk",
    quantity: 50.0,
    unit: "liters",
    selling_price: 3.50,
    cost_price: 2.50,
    expiry_date: "2024-02-15"
};

fetch('/api/v1/items', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(itemData)
})
.then(response => response.json())
.then(data => {
    console.log('Item created:', data.message);
    console.log('Item details:', data.item);
});
```

### Check Item Existence

```javascript
fetch('/api/v1/items/check', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({ name: "Organic Milk" })
})
.then(response => response.json())
.then(data => {
    if (data.exists) {
        console.log('Item exists:', data.item);
    } else {
        console.log('Item does not exist');
    }
});
```

### Filter Items

```javascript
const params = new URLSearchParams({
    search: 'milk',
    status: 'expiring_soon',
    price_range: 'cost_under_50',
    sort_by: 'expiry_date',
    sort_order: 'asc'
});

fetch(`/api/v1/items/filter?${params}`)
.then(response => response.json())
.then(data => {
    console.log('Filtered items:', data);
});
```

### Update Item

```javascript
const updateData = {
    name: "Updated Milk",
    quantity: 75.0,
    expiry_date: "2024-03-15"
};

fetch('/api/v1/items/123', {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify(updateData)
})
.then(response => response.json())
.then(data => {
    console.log('Item updated:', data.message);
    console.log('Updated item:', data.item);
});
```

### Delete Item

```javascript
fetch('/api/v1/items/123', {
    method: 'DELETE',
    headers: {
        'X-CSRFToken': csrfToken
    }
})
.then(response => response.json())
.then(data => {
    console.log('Item deleted:', data.message);
});
```

### Bulk Delete Items

```javascript
fetch('/api/v1/items/bulk-delete', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        item_ids: [1, 2, 3, 4, 5]
    })
})
.then(response => response.json())
.then(data => {
    console.log('Bulk delete result:', data.message);
});
```

---

**Previous**: [Authentication Routes](./authentication.md) | **Next**: [Notifications API](./notifications.md) 