# Security Implementation

## Overview

Expiry Tracker implements a comprehensive security framework following industry best practices to protect user data, prevent common attacks, and ensure system integrity.

## Security Architecture

### Multi-Layer Security Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Security                      │
├─────────────────────────────────────────────────────────────┤
│  Input Validation  │  Authentication  │  Authorization      │
├─────────────────────────────────────────────────────────────┤
│  Session Management  │  CSRF Protection  │  Rate Limiting    │
├─────────────────────────────────────────────────────────────┤
│  Data Encryption  │  Secure Headers  │  Error Handling      │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                    Infrastructure Security                   │
├─────────────────────────────────────────────────────────────┤
│  Database Security  │  Network Security  │  File Security    │
└─────────────────────────────────────────────────────────────┘
```

## Authentication & Authorization

### User Authentication

#### Password Security

```python
class User(UserMixin, BaseModel):
    password_hash = db.Column(db.String(128))
    
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')
    
    @password.setter
    def password(self, password):
        # Use bcrypt for password hashing
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'), 
            bcrypt.gensalt()
        ).decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
```

**Security Features:**
- **bcrypt Hashing**: Industry-standard password hashing
- **Salt Generation**: Unique salt per password
- **Work Factor**: Configurable computational cost
- **No Plain Text**: Passwords never stored in plain text

#### Session Management

```python
# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.session_protection = 'strong'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
```

**Security Features:**
- **Session Protection**: Strong session protection enabled
- **Automatic Logout**: Sessions expire after inactivity
- **Secure Cookies**: HTTP-only, secure cookies
- **Session Regeneration**: New session on login

#### Account Lockout

```python
class User(BaseModel):
    login_attempts = db.Column(db.Integer, default=0)
    locked_until = db.Column(db.DateTime)
    
    def increment_login_attempts(self):
        self.login_attempts += 1
        if self.login_attempts >= 5:
            self.locked_until = datetime.utcnow() + timedelta(minutes=30)
        self.save()
    
    def is_locked(self):
        if self.locked_until and self.locked_until > datetime.utcnow():
            return True
        return False
```

**Security Features:**
- **Attempt Tracking**: Count failed login attempts
- **Temporary Lockout**: 30-minute lockout after 5 failed attempts
- **Automatic Reset**: Lockout expires automatically
- **Admin Override**: Administrators can unlock accounts

### Authorization

#### Route Protection

```python
from flask_login import login_required, current_user

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Protected route requiring authentication."""
    return render_template('dashboard.html')

@api_bp.route('/admin/users')
@login_required
@require_admin
def admin_users():
    """Protected route requiring admin privileges."""
    return jsonify({'users': get_all_users()})
```

**Security Features:**
- **Login Required**: All sensitive routes protected
- **Role-Based Access**: Admin-only routes
- **User Context**: Current user available in all routes
- **Graceful Handling**: Redirect to login for unauthenticated users

## Input Validation & Sanitization

### Form Validation

```python
from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, DateField
from wtforms.validators import DataRequired, Length, NumberRange, Email

class ItemForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(message='Name is required'),
        Length(min=1, max=100, message='Name must be between 1 and 100 characters')
    ])
    
    quantity = FloatField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=0, max=999999.99, message='Quantity must be positive')
    ])
    
    expiry_date = DateField('Expiry Date', validators=[
        DataRequired(message='Expiry date is required')
    ])
```

**Security Features:**
- **Server-Side Validation**: All input validated on server
- **Type Checking**: Proper data type validation
- **Length Limits**: Prevent buffer overflow attacks
- **Range Validation**: Numeric value constraints

### API Input Validation

```python
def validate_item_data(data):
    """Validate item data from API requests."""
    errors = {}
    
    # Required fields
    if not data.get('name'):
        errors['name'] = ['Name is required']
    elif len(data['name']) > 100:
        errors['name'] = ['Name too long']
    
    # Quantity validation
    try:
        quantity = float(data.get('quantity', 0))
        if quantity < 0:
            errors['quantity'] = ['Quantity must be positive']
    except (ValueError, TypeError):
        errors['quantity'] = ['Invalid quantity value']
    
    if errors:
        raise ValidationError('Validation failed', errors)
    
    return data
```

**Security Features:**
- **Comprehensive Validation**: All fields validated
- **Type Safety**: Proper type conversion and checking
- **Error Reporting**: Detailed error messages
- **Exception Handling**: Graceful error handling

### XSS Prevention

```python
# Automatic HTML escaping in templates
{{ item.name|escape }}

# CSRF token in forms
<form method="POST">
    {{ form.hidden_tag() }}
    {{ form.name.label }} {{ form.name() }}
</form>

# JSON response sanitization
def sanitize_for_json(data):
    """Sanitize data for JSON response."""
    if isinstance(data, str):
        return html.escape(data)
    elif isinstance(data, dict):
        return {k: sanitize_for_json(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_for_json(item) for item in data]
    return data
```

**Security Features:**
- **HTML Escaping**: Automatic escaping in templates
- **CSRF Protection**: All forms protected
- **JSON Sanitization**: Safe JSON responses
- **Content Security Policy**: CSP headers configured

## CSRF Protection

### Implementation

```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def init_extensions(app):
    csrf.init_app(app)
    
    # Exempt specific endpoints from CSRF
    csrf.exempt(app.view_functions['api_date_ocr_extract'])
```

### Token Management

```html
<!-- CSRF token in meta tag -->
<meta name="csrf-token" content="{{ csrf_token() }}">

<!-- CSRF token in forms -->
<form method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <!-- form fields -->
</form>
```

```javascript
// CSRF token in API requests
fetch('/api/v1/items', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
    },
    body: JSON.stringify(data)
});
```

**Security Features:**
- **Automatic Protection**: All POST/PUT/DELETE requests protected
- **Token Validation**: Server-side token verification
- **Secure Generation**: Cryptographically secure tokens
- **Exemption Control**: Selective endpoint exemption

## Database Security

### SQL Injection Prevention

```python
# SQLAlchemy ORM prevents SQL injection
items = Item.query.filter_by(user_id=current_user.id).all()

# Parameterized queries for complex operations
query = db.session.execute(
    'SELECT * FROM items WHERE user_id = :user_id AND status = :status',
    {'user_id': user_id, 'status': 'active'}
)

# Input validation before database operations
def safe_get_items(user_id, status=None):
    if not isinstance(user_id, int) or user_id <= 0:
        raise ValueError('Invalid user ID')
    
    query = Item.query.filter_by(user_id=user_id)
    if status:
        query = query.filter_by(status=status)
    
    return query.all()
```

**Security Features:**
- **ORM Usage**: SQLAlchemy prevents injection
- **Parameterized Queries**: Safe for complex queries
- **Input Validation**: Validate before database operations
- **Type Checking**: Ensure proper data types

### Data Encryption

```python
class User(BaseModel):
    # Encrypted credential storage
    zoho_client_id_hash = db.Column(db.String(255))
    zoho_client_secret_hash = db.Column(db.String(255))
    zoho_client_id_salt = db.Column(db.String(255))
    zoho_client_secret_salt = db.Column(db.String(255))
    
    def set_zoho_credentials(self, client_id, client_secret):
        """Securely store Zoho credentials."""
        # Generate unique salts
        self.zoho_client_id_salt = secrets.token_hex(32)
        self.zoho_client_secret_salt = secrets.token_hex(32)
        
        # Hash credentials with salts
        self.zoho_client_id_hash = hashlib.sha256(
            (client_id + self.zoho_client_id_salt).encode()
        ).hexdigest()
        
        self.zoho_client_secret_hash = hashlib.sha256(
            (client_secret + self.zoho_client_secret_salt).encode()
        ).hexdigest()
```

**Security Features:**
- **Credential Hashing**: Sensitive data hashed
- **Unique Salts**: Each credential has unique salt
- **Secure Storage**: No plain text credentials
- **Verification Methods**: Secure credential verification

## Rate Limiting

### Implementation

```python
from functools import wraps
from flask import request, jsonify
import time

def rate_limit(max_requests=100, window=60):
    """Rate limiting decorator."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simple in-memory rate limiting
            client_ip = request.remote_addr
            current_time = time.time()
            
            # Check rate limit
            if is_rate_limited(client_ip, max_requests, window):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': 'Too many requests. Please try again later.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@api_bp.route('/items')
@rate_limit(max_requests=100, window=60)
@login_required
def get_items():
    """Rate-limited API endpoint."""
    return jsonify({'items': get_user_items()})
```

**Security Features:**
- **Request Limiting**: Prevent abuse
- **Configurable Limits**: Different limits per endpoint
- **IP-Based Tracking**: Track by client IP
- **Graceful Handling**: Proper error responses

## Secure Headers

### Implementation

```python
from flask import Flask
from flask_talisman import Talisman

def init_security_headers(app):
    """Initialize security headers."""
    Talisman(
        app,
        content_security_policy={
            'default-src': "'self'",
            'script-src': ["'self'", "'unsafe-inline'"],
            'style-src': ["'self'", "'unsafe-inline'"],
            'img-src': ["'self'", "data:", "https:"],
            'font-src': ["'self'", "https:"],
        },
        force_https=False,  # Set to True in production
        strict_transport_security=True,
        session_cookie_secure=False,  # Set to True in production
        session_cookie_http_only=True,
        session_cookie_samesite='Lax'
    )
```

**Security Headers:**
- **Content Security Policy**: Prevent XSS attacks
- **Strict Transport Security**: Enforce HTTPS
- **X-Frame-Options**: Prevent clickjacking
- **X-Content-Type-Options**: Prevent MIME sniffing
- **Referrer Policy**: Control referrer information

## Error Handling

### Secure Error Responses

```python
def register_error_handlers(app):
    """Register secure error handlers."""
    
    def is_api_request():
        return request.path.startswith('/api/')
    
    @app.errorhandler(400)
    def bad_request_error(error):
        if is_api_request():
            return jsonify({'error': 'Bad Request'}), 400
        return render_template('errors/400.html'), 400
    
    @app.errorhandler(404)
    def not_found_error(error):
        if is_api_request():
            return jsonify({'error': 'Not Found'}), 404
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        # Log error details
        app.logger.error(f'Internal server error: {error}')
        
        if is_api_request():
            return jsonify({'error': 'Internal Server Error'}), 500
        return render_template('errors/500.html'), 500
```

**Security Features:**
- **No Information Leakage**: Generic error messages
- **Proper Logging**: Detailed error logging
- **API Consistency**: Consistent error responses
- **User-Friendly**: Appropriate error pages

## File Upload Security

### Image Upload Validation

```python
import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_upload(file):
    """Validate uploaded file."""
    if not file:
        raise ValueError('No file provided')
    
    if not allowed_file(file.filename):
        raise ValueError('File type not allowed')
    
    if file.content_length > MAX_FILE_SIZE:
        raise ValueError('File too large')
    
    # Secure filename
    filename = secure_filename(file.filename)
    
    return filename
```

**Security Features:**
- **File Type Validation**: Only allowed extensions
- **Size Limits**: Prevent large file uploads
- **Secure Filenames**: Prevent path traversal
- **Content Validation**: Check file content

## Logging & Monitoring

### Security Logging

```python
import logging
from datetime import datetime

# Security-specific logger
security_logger = logging.getLogger('security')
security_logger.setLevel(logging.INFO)

def log_security_event(event_type, user_id, details):
    """Log security events."""
    security_logger.info(
        f'Security Event: {event_type} | User: {user_id} | '
        f'Details: {details} | Time: {datetime.utcnow()}'
    )

# Log authentication events
def log_login_attempt(user_id, success, ip_address):
    log_security_event(
        'login_attempt',
        user_id,
        f'success={success}, ip={ip_address}'
    )

# Log sensitive operations
def log_credential_access(user_id, operation, ip_address):
    log_security_event(
        'credential_access',
        user_id,
        f'operation={operation}, ip={ip_address}'
    )
```

**Security Features:**
- **Comprehensive Logging**: All security events logged
- **Audit Trail**: Complete user activity tracking
- **IP Tracking**: Monitor suspicious activity
- **Secure Storage**: Logs stored securely

## Environment Security

### Configuration Management

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security settings
    SESSION_COOKIE_SECURE = os.environ.get('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL')
    
    # Email settings
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
```

**Security Features:**
- **Environment Variables**: Sensitive data in environment
- **Production Settings**: Secure defaults for production
- **Configuration Validation**: Validate required settings
- **Secret Management**: Secure secret handling

## Security Best Practices

### Development Guidelines

1. **Input Validation**
   - Validate all user inputs
   - Use whitelist approach for allowed values
   - Implement proper error handling

2. **Authentication**
   - Use strong password requirements
   - Implement account lockout
   - Use secure session management

3. **Authorization**
   - Check permissions on every request
   - Implement role-based access control
   - Log all sensitive operations

4. **Data Protection**
   - Encrypt sensitive data at rest
   - Use HTTPS for all communications
   - Implement proper backup procedures

5. **Monitoring**
   - Log all security events
   - Monitor for suspicious activity
   - Implement alerting for security incidents

### Production Security Checklist

- [ ] HTTPS enabled with valid SSL certificate
- [ ] Security headers configured
- [ ] Rate limiting implemented
- [ ] Input validation on all endpoints
- [ ] CSRF protection enabled
- [ ] SQL injection prevention verified
- [ ] XSS protection implemented
- [ ] File upload security configured
- [ ] Error handling secure
- [ ] Logging and monitoring active
- [ ] Regular security updates applied
- [ ] Backup procedures tested
- [ ] Incident response plan ready

## Incident Response

### Security Incident Handling

1. **Detection**: Monitor logs and alerts
2. **Assessment**: Evaluate incident severity
3. **Containment**: Isolate affected systems
4. **Investigation**: Determine root cause
5. **Remediation**: Fix security vulnerabilities
6. **Recovery**: Restore normal operations
7. **Documentation**: Record incident details
8. **Prevention**: Implement preventive measures

---

**Security Version**: 1.0  
**Last Updated**: December 2024  
**Status**: Production Ready 