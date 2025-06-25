# Authentication Routes

This document covers the Authentication routes for user registration, login, and account management.

## Overview

The Authentication routes provide endpoints for user registration, login, email verification, password reset, and account management. Most endpoints are accessible without authentication, except for logout and Zoho integration. These are web routes that handle form submissions and redirects, not API endpoints returning JSON responses.

## Endpoints

### User Registration

**POST** `/auth/register`

Register a new user account.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `username`: Username (3-20 characters, letters and numbers only)
- `email`: Email address
- `password`: Password (minimum 8 characters, include uppercase, lowercase, number)
- `confirm_password`: Password confirmation
- `csrf_token`: CSRF token

**Response:**
```json
{
  "success": true,
  "message": "Registration successful! Please check your email to verify your account.",
  "redirect": "/auth/verify-email"
}
```

**Error Response:**
```json
{
  "success": false,
  "message": "Username already taken."
}
```

### User Login

**POST** `/auth/login`

Authenticate user and create session.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `email`: Email address
- `password`: Password
- `remember_me`: Remember me checkbox (optional)
- `csrf_token`: CSRF token

**Response:**
- Redirects to dashboard on success
- Returns login form with errors on failure

### Email Verification

**POST** `/auth/verify-email`

Verify user email address with verification code.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `verification_code`: Email verification code
- `csrf_token`: CSRF token

**Response:**
- Redirects to login on success
- Returns verification form with errors on failure

### Resend Verification Email

**POST** `/auth/resend-verification`

Resend email verification code.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `csrf_token`: CSRF token

**Response:**
- Success message with new verification code sent
- Error message if resend fails

### Forgot Password

**POST** `/auth/forgot-password`

Request password reset email.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `email`: Email address
- `csrf_token`: CSRF token

**Response:**
- Success message with reset email sent
- Error message if email not found

### Reset Password

**POST** `/auth/reset_password/{token}`

Reset password using reset token.

**Request Body:**
```
Content-Type: application/x-www-form-urlencoded
```

**Form Data:**
- `password`: New password
- `confirm_password`: Password confirmation
- `csrf_token`: CSRF token

**Response:**
- Redirects to login on success
- Returns reset form with errors on failure

### User Logout

**GET** `/auth/logout`

Logout user and destroy session.

**Authentication**: Required

**Response:**
- Redirects to home page

### Zoho Integration

**GET** `/auth/zoho/auth`

Initiate Zoho OAuth authorization.

**Authentication**: Required

**Response:**
- Redirects to Zoho authorization page

**GET** `/auth/zoho/callback`

Handle Zoho OAuth callback.

**Authentication**: Required

**Response:**
- Redirects to settings page on success
- Error page on failure

## Form Validation

### Registration Validation

- **Username**: 3-20 characters, letters and numbers only
- **Email**: Valid email format
- **Password**: Minimum 8 characters, include uppercase, lowercase, number
- **Confirm Password**: Must match password

### Login Validation

- **Email**: Valid email format
- **Password**: Required

### Password Reset Validation

- **Email**: Valid email format
- **New Password**: Minimum 8 characters, include uppercase, lowercase, number
- **Confirm Password**: Must match new password

## Error Responses

### Registration Errors

```json
{
  "success": false,
  "message": "Username already taken."
}
```

```json
{
  "success": false,
  "message": "Email already registered."
}
```

```json
{
  "success": false,
  "message": "Passwords do not match."
}
```

### Login Errors

- **Invalid credentials**: "Invalid email or password"
- **Account locked**: "Account is locked. Please try again in X minutes."
- **Unverified account**: "Please verify your email address to continue."

### Verification Errors

- **Invalid code**: "Invalid verification code"
- **Expired code**: "Verification code has expired"

## Security Features

### Account Protection

- **Login attempts**: Limited to 5 attempts before lockout
- **Lockout duration**: 30 minutes after exceeding limit
- **Email verification**: Required before login
- **Password strength**: Enforced during registration and reset

### Session Management

- **Session timeout**: 15 minutes of inactivity
- **Remember me**: Extends session to 24 hours
- **CSRF protection**: All forms require CSRF token

### Password Security

- **Minimum length**: 8 characters
- **Complexity requirements**: Uppercase, lowercase, number
- **Secure reset**: Email-based with time-limited tokens

## Usage Examples

### Register New User

```javascript
const formData = new FormData();
formData.append('username', 'newuser');
formData.append('email', 'user@example.com');
formData.append('password', 'SecurePass123');
formData.append('confirm_password', 'SecurePass123');
formData.append('csrf_token', csrfToken);

fetch('/auth/register', {
  method: 'POST',
  body: formData,
  headers: {
    'X-Requested-With': 'XMLHttpRequest'
  }
})
.then(response => response.json())
.then(data => {
  if (data.success) {
    console.log('Registration successful:', data.message);
    window.location.href = data.redirect;
  } else {
    console.error('Registration failed:', data.message);
  }
});
```

### Login User

```javascript
const formData = new FormData();
formData.append('email', 'user@example.com');
formData.append('password', 'SecurePass123');
formData.append('remember_me', 'on');
formData.append('csrf_token', csrfToken);

fetch('/auth/login', {
  method: 'POST',
  body: formData
})
.then(response => {
  if (response.redirected) {
    window.location.href = response.url;
  } else {
    return response.text();
  }
})
.then(html => {
  // Handle login errors
  console.log('Login failed, showing form with errors');
});
```

### Verify Email

```javascript
const formData = new FormData();
formData.append('verification_code', '123456');
formData.append('csrf_token', csrfToken);

fetch('/auth/verify-email', {
  method: 'POST',
  body: formData
})
.then(response => {
  if (response.redirected) {
    window.location.href = response.url;
  }
});
```

### Request Password Reset

```javascript
const formData = new FormData();
formData.append('email', 'user@example.com');
formData.append('csrf_token', csrfToken);

fetch('/auth/forgot-password', {
  method: 'POST',
  body: formData
})
.then(response => response.text())
.then(html => {
  console.log('Password reset email sent');
});
```

## Frontend Integration

### Real-time Validation

The frontend includes real-time validation for all forms:

```javascript
// Username validation
function validateUsername(value) {
  if (!value.trim()) return 'Username is required';
  if (value.length < 3) return 'Username must be at least 3 characters';
  if (value.length > 20) return 'Username must be 20 characters or less';
  if (!/^[a-zA-Z0-9]+$/.test(value)) return 'Username can only contain letters and numbers';
  return null;
}

// Email validation
function validateEmail(value) {
  if (!value.trim()) return 'Email is required';
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(value)) return 'Please enter a valid email address';
  return null;
}

// Password validation
function validatePassword(value) {
  if (!value) return 'Password is required';
  if (value.length < 8) return 'Password must be at least 8 characters';
  if (!/(?=.*[a-z])/.test(value)) return 'Password must contain at least one lowercase letter';
  if (!/(?=.*[A-Z])/.test(value)) return 'Password must contain at least one uppercase letter';
  if (!/(?=.*\d)/.test(value)) return 'Password must contain at least one number';
  return null;
}
```

### Form Sanitization

All user inputs are sanitized to prevent XSS:

```javascript
function sanitizeInput(value) {
  return value.replace(/<[^>]*>/g, '').trim();
}
```

## Implementation Note

These endpoints are implemented as web routes in `app/routes/auth.py` and handle form submissions, redirects, and HTML responses. They are not API endpoints returning JSON responses, but rather traditional web routes that support both form submissions and AJAX requests.

---

**Previous**: [Activities API](./activities.md) | **Next**: [Items API](./items.md) 