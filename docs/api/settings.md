# Settings API

This document covers the Settings API endpoints for managing user preferences, Zoho integration, and account settings.

## Overview

The Settings API provides endpoints for managing user account settings, Zoho integration credentials, and notification preferences. All endpoints require authentication.

## Authentication

All endpoints require a valid session cookie. Include the CSRF token in request headers for POST/PUT/DELETE requests.

**Headers:**
```
X-CSRFToken: <csrf_token>
Content-Type: application/json
```

## Endpoints

### Update Notification Settings

**PUT** `/api/v1/settings/notifications`

Update email notification preferences.

**Request Body:**
```json
{
  "email_notifications": true
}
```

**Response:**
```json
{
  "message": "Notification settings updated successfully",
  "email_notifications": true
}
```

### Update Zoho Credentials

**PUT** `/api/v1/settings/zoho-credentials`

Save Zoho Client ID and Client Secret credentials.

**Request Body:**
```json
{
  "zoho_client_id": "your_client_id",
  "zoho_client_secret": "your_client_secret"
}
```

**Response:**
```json
{
  "message": "Zoho credentials updated successfully"
}
```

### Disconnect from Zoho

**DELETE** `/api/v1/settings/disconnect-zoho`

Disconnect Zoho integration and remove stored credentials.

**Request Body:**
```json
{
  "password": "user_password"
}
```

**Response:**
```json
{
  "message": "Successfully disconnected from Zoho"
}
```

### Get Zoho Credential

**POST** `/api/v1/settings/get-zoho-credential`

Retrieve a specific Zoho credential (requires password and email verification).

**Request Body:**
```json
{
  "credential_type": "zoho_client_id",
  "password": "user_password",
  "email_code": "verification_code"
}
```

**Response:**
```json
{
  "success": true,
  "credential": "actual_credential_value"
}
```

### Request Credential Access Code

**POST** `/api/v1/settings/request-credential-access-code`

Request email verification code to access credentials.

**Request Body:**
```json
{}
```

**Response:**
```json
{
  "message": "Verification code sent to your email"
}
```

### Verify Credential Access

**POST** `/api/v1/settings/verify-credential-access`

Verify password and email code to access credentials.

**Request Body:**
```json
{
  "credential_type": "zoho_client_id",
  "password": "user_password",
  "email_code": "verification_code"
}
```

**Response:**
```json
{
  "success": true,
  "credential": "actual_credential_value"
}
```

### Request Enhanced Disconnect Code

**POST** `/api/v1/settings/request-enhanced-disconnect-code`

Request email verification code for enhanced disconnect.

**Request Body:**
```json
{
  "password": "user_password"
}
```

**Response:**
```json
{
  "message": "Verification code sent to your email"
}
```

### Verify Enhanced Disconnect

**POST** `/api/v1/settings/verify-enhanced-disconnect`

Verify password and email code for enhanced disconnect.

**Request Body:**
```json
{
  "password": "user_password",
  "email_code": "verification_code",
  "zoho_client_id": "your_client_id",
  "zoho_client_secret": "your_client_secret"
}
```

**Response:**
```json
{
  "message": "Successfully disconnected from Zoho"
}
```

### Request Report Deletion Code

**POST** `/api/v1/settings/request-report-deletion-code`

Request email verification code for report deletion.

**Request Body:**
```json
{
  "password": "user_password"
}
```

**Response:**
```json
{
  "message": "Verification code sent to your email"
}
```

### Verify Report Deletion

**POST** `/api/v1/settings/verify-report-deletion`

Verify password and email code for report deletion.

**Request Body:**
```json
{
  "password": "user_password",
  "email_code": "verification_code",
  "report_id": 123
}
```

**Response:**
```json
{
  "message": "Report deleted successfully"
}
```

### Get Credential Access Logs

**GET** `/api/v1/settings/credential-access-logs`

Get logs of credential access attempts.

**Response:**
```json
{
  "logs": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "action": "view_credential",
      "credential_type": "zoho_client_id",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

## Error Responses

### Invalid Credentials

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Invalid password"
}
```

### Rate Limit Exceeded

```http
HTTP/1.1 429 Too Many Requests
Content-Type: application/json

{
  "error": "Rate limit exceeded. Try again in 15 minutes."
}
```

### Missing Required Fields

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "Both Zoho Client ID and Client Secret are required"
}
```

### Credential Already in Use

```http
HTTP/1.1 409 Conflict
Content-Type: application/json

{
  "error": "These Zoho credentials are already being used by another user"
}
```

## Usage Examples

### Update Notification Settings

```javascript
fetch('/api/v1/settings/notifications', {
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
  console.log('Settings updated:', data.message);
});
```

### Save Zoho Credentials

```javascript
fetch('/api/v1/settings/zoho-credentials', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({
    zoho_client_id: 'your_client_id',
    zoho_client_secret: 'your_client_secret'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Credentials saved:', data.message);
});
```

### View Credential with Verification

```javascript
// First request verification code
fetch('/api/v1/settings/request-credential-access-code', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRFToken': csrfToken
  },
  body: JSON.stringify({})
})
.then(response => response.json())
.then(data => {
  console.log('Code sent:', data.message);
  
  // Then verify and get credential
  return fetch('/api/v1/settings/verify-credential-access', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
      credential_type: 'zoho_client_id',
      password: 'user_password',
      email_code: '123456'
    })
  });
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Credential:', data.credential);
  }
});
```

## Security Features

### Rate Limiting

- **Email code requests**: 5 attempts per 15 minutes
- **Verification attempts**: 5 attempts per 15 minutes
- **Enhanced disconnect**: 5 attempts per 15 minutes
- **Report deletion**: 3 attempts per 15 minutes

### Credential Security

- Credentials are encrypted using AES-256
- Access requires password verification
- Email verification code required for sensitive operations
- Access is logged and monitored
- Credentials auto-hide after 30 seconds

### Session Management

- Session expires after 15 minutes of inactivity
- Remember me option extends session to 24 hours
- Account lockout after failed attempts

---

**Previous**: [Reports API](./reports.md) | **Next**: [Date OCR API](./date-ocr.md) 