# Database Schema

This document provides a comprehensive overview of the database schema for the Expiry Tracker application.

## Overview

The application uses SQLAlchemy ORM with PostgreSQL as the primary database. The schema is designed to support multi-tenant inventory management with user isolation, activity tracking, and notification systems.

## Database Configuration

### Environment Variables

```bash
# Database Configuration
DATABASE_URL=postgresql://username:password@localhost/expiry_tracker
SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost/expiry_tracker
SQLALCHEMY_TRACK_MODIFICATIONS=False
```

### Connection Setup

The database connection is managed through Flask-SQLAlchemy with the following configuration:

```python
# app/config.py
class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://username:password@localhost/expiry_tracker'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

## Core Tables

### Users Table

**Table Name:** `users`

**Purpose:** Stores user account information and authentication details.

**Schema:**
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email_verified BOOLEAN DEFAULT FALSE,
    email_verification_token VARCHAR(255),
    reset_password_token VARCHAR(255),
    reset_password_expires TIMESTAMP,
    zoho_access_token TEXT,
    zoho_refresh_token TEXT,
    zoho_organization_id VARCHAR(255),
    zoho_organization_name VARCHAR(255),
    zoho_credentials_encrypted TEXT,
    zoho_credentials_salt VARCHAR(255),
    zoho_credentials_iv VARCHAR(255),
    zoho_disconnect_email_code VARCHAR(255),
    zoho_disconnect_email_code_expires TIMESTAMP,
    email_notifications BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**
- `id`: Primary key, auto-incrementing
- `username`: Unique username for login
- `email`: Unique email address
- `password_hash`: Hashed password using bcrypt
- `email_verified`: Email verification status
- `zoho_*`: Zoho integration credentials (encrypted)
- `email_notifications`: User preference for email notifications

**Indexes:**
```sql
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email_verified ON users(email_verified);
```

### Items Table

**Table Name:** `items`

**Purpose:** Stores inventory items with expiry tracking.

**Schema:**
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity DECIMAL(10,2) NOT NULL DEFAULT 0,
    unit VARCHAR(20) NOT NULL,
    selling_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    expiry_date DATE,
    status VARCHAR(20) DEFAULT 'active',
    zoho_item_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**
- `id`: Primary key, auto-incrementing
- `user_id`: Foreign key to users table
- `name`: Item name (unique per user)
- `quantity`: Current stock quantity
- `unit`: Unit of measurement
- `selling_price`: Retail price
- `cost_price`: Purchase cost
- `expiry_date`: Expiration date
- `status`: Item status (active, expired, expiring_soon, pending)
- `zoho_item_id`: External Zoho CRM item ID

**Indexes:**
```sql
CREATE INDEX idx_items_user_id ON items(user_id);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_items_expiry_date ON items(expiry_date);
CREATE INDEX idx_items_name_user ON items(name, user_id);
CREATE INDEX idx_items_zoho_id ON items(zoho_item_id);
```

### Activities Table

**Table Name:** `activities`

**Purpose:** Tracks user activities and system events for audit trail.

**Schema:**
```sql
CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    activity_type VARCHAR(50) NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    activity_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**
- `id`: Primary key, auto-incrementing
- `user_id`: Foreign key to users table
- `activity_type`: Type of activity (item_added, item_updated, etc.)
- `title`: Activity title
- `description`: Detailed description
- `activity_data`: JSON data with additional context
- `created_at`: Timestamp of activity

**Indexes:**
```sql
CREATE INDEX idx_activities_user_id ON activities(user_id);
CREATE INDEX idx_activities_type ON activities(activity_type);
CREATE INDEX idx_activities_created_at ON activities(created_at);
CREATE INDEX idx_activities_user_type ON activities(user_id, activity_type);
```

### Notifications Table

**Table Name:** `notifications`

**Purpose:** Stores email notifications and their delivery status.

**Schema:**
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    item_id INTEGER REFERENCES items(id) ON DELETE SET NULL,
    message TEXT NOT NULL,
    type VARCHAR(20) DEFAULT 'email',
    status VARCHAR(20) DEFAULT 'pending',
    priority VARCHAR(20) DEFAULT 'normal',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at TIMESTAMP
);
```

**Key Fields:**
- `id`: Primary key, auto-incrementing
- `user_id`: Foreign key to users table
- `item_id`: Related item (optional)
- `message`: Notification message
- `type`: Notification type (email, sms, etc.)
- `status`: Delivery status (pending, sent, failed)
- `priority`: Priority level (low, normal, high)
- `sent_at`: Timestamp when notification was sent

**Indexes:**
```sql
CREATE INDEX idx_notifications_user_id ON notifications(user_id);
CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_created_at ON notifications(created_at);
CREATE INDEX idx_notifications_item_id ON notifications(item_id);
```

### Reports Table

**Table Name:** `reports`

**Purpose:** Stores generated inventory reports with historical data.

**Schema:**
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    report_date DATE NOT NULL,
    total_items INTEGER NOT NULL DEFAULT 0,
    active_items INTEGER NOT NULL DEFAULT 0,
    expiring_items INTEGER NOT NULL DEFAULT 0,
    expired_items INTEGER NOT NULL DEFAULT 0,
    total_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    active_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    expiring_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    expired_value DECIMAL(12,2) NOT NULL DEFAULT 0,
    report_data JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Key Fields:**
- `id`: Primary key, auto-incrementing
- `user_id`: Foreign key to users table
- `report_date`: Date for which report was generated
- `total_items`: Total number of items
- `active_items`: Number of active items
- `expiring_items`: Number of items expiring soon
- `expired_items`: Number of expired items
- `total_value`: Total inventory value
- `active_value`: Value of active items
- `expiring_value`: Value of expiring items
- `expired_value`: Value of expired items
- `report_data`: JSON data with detailed report information

**Indexes:**
```sql
CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_date ON reports(report_date);
CREATE INDEX idx_reports_user_date ON reports(user_id, report_date);
```

## Relationships

### One-to-Many Relationships

1. **User → Items**: One user can have many items
2. **User → Activities**: One user can have many activities
3. **User → Notifications**: One user can have many notifications
4. **User → Reports**: One user can have many reports

### Foreign Key Constraints

```sql
-- Items table
ALTER TABLE items ADD CONSTRAINT fk_items_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Activities table
ALTER TABLE activities ADD CONSTRAINT fk_activities_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;

-- Notifications table
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
ALTER TABLE notifications ADD CONSTRAINT fk_notifications_item 
    FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE SET NULL;

-- Reports table
ALTER TABLE reports ADD CONSTRAINT fk_reports_user 
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
```

## Data Types and Constraints

### String Fields
- **VARCHAR(80)**: Usernames, short text fields
- **VARCHAR(120)**: Email addresses
- **VARCHAR(255)**: Tokens, IDs, longer text fields
- **TEXT**: Descriptions, messages, encrypted data

### Numeric Fields
- **DECIMAL(10,2)**: Prices, quantities with 2 decimal places
- **DECIMAL(12,2)**: Report values with 2 decimal places
- **INTEGER**: Counts, IDs, status codes

### Date/Time Fields
- **DATE**: Expiry dates, report dates
- **TIMESTAMP**: Created/updated timestamps, token expiration

### Boolean Fields
- **BOOLEAN**: Flags, preferences, verification status

### JSON Fields
- **JSONB**: Activity data, report data, flexible schema data

## Constraints

### Unique Constraints
```sql
-- Users table
ALTER TABLE users ADD CONSTRAINT unique_username UNIQUE (username);
ALTER TABLE users ADD CONSTRAINT unique_email UNIQUE (email);

-- Items table (per user)
ALTER TABLE items ADD CONSTRAINT unique_item_name_per_user UNIQUE (name, user_id);

-- Reports table (per user per date)
ALTER TABLE reports ADD CONSTRAINT unique_report_per_user_date UNIQUE (user_id, report_date);
```

### Check Constraints
```sql
-- Items table
ALTER TABLE items ADD CONSTRAINT check_quantity_positive CHECK (quantity >= 0);
ALTER TABLE items ADD CONSTRAINT check_prices_positive CHECK (selling_price >= 0 AND cost_price >= 0);
ALTER TABLE items ADD CONSTRAINT check_valid_status CHECK (status IN ('active', 'expired', 'expiring_soon', 'pending'));

-- Notifications table
ALTER TABLE notifications ADD CONSTRAINT check_valid_notification_status CHECK (status IN ('pending', 'sent', 'failed'));
ALTER TABLE notifications ADD CONSTRAINT check_valid_notification_type CHECK (type IN ('email', 'sms', 'push'));
ALTER TABLE notifications ADD CONSTRAINT check_valid_priority CHECK (priority IN ('low', 'normal', 'high'));

-- Activities table
ALTER TABLE activities ADD CONSTRAINT check_valid_activity_type CHECK (activity_type IN (
    'item_added', 'item_updated', 'item_deleted', 'expiry_alert', 
    'notification_sent', 'report_generated', 'settings_updated', 
    'zoho_sync', 'login', 'logout'
));
```

## Migration Management

### Alembic Migrations

The application uses Alembic for database migrations:

```bash
# Initialize migrations
alembic init migrations

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration Files Location
```
migrations/
├── alembic.ini
├── env.py
├── README
├── script.py.mako
└── versions/
    ├── initial_migration.py
    ├── add_security_fields.py
    ├── add_zoho_credential_hashing_fields.py
    └── ...
```

## Performance Considerations

### Indexing Strategy

1. **Primary Keys**: All tables have auto-incrementing primary keys
2. **Foreign Keys**: Indexed for join performance
3. **Query Patterns**: Indexes on frequently queried fields
4. **Composite Indexes**: For multi-field queries (user_id + status)

### Query Optimization

1. **User Isolation**: All queries filter by user_id for security
2. **Status Filtering**: Indexes on status fields for quick filtering
3. **Date Range Queries**: Indexes on date fields for time-based queries
4. **Text Search**: Full-text search capabilities for item names and descriptions

### Data Retention

1. **Activities**: Keep for audit trail (configurable retention period)
2. **Notifications**: Clean up old notifications periodically
3. **Reports**: Keep historical reports for trend analysis
4. **Items**: Soft delete or archive old items

## Security Considerations

### Data Encryption

1. **Zoho Credentials**: Encrypted using AES-256 with salt and IV
2. **Passwords**: Hashed using bcrypt with salt
3. **Tokens**: Stored as hashed values where possible

### Access Control

1. **Row-Level Security**: All queries filter by user_id
2. **Foreign Key Constraints**: Prevent orphaned records
3. **Input Validation**: Server-side validation for all inputs

### Backup Strategy

1. **Regular Backups**: Automated daily backups
2. **Point-in-Time Recovery**: Transaction log backups
3. **Encrypted Backups**: Backup files encrypted at rest
4. **Offsite Storage**: Backups stored in multiple locations

---

**Previous**: [Architecture Overview](./architecture.md) | **Next**: [Services Layer](./services.md) 