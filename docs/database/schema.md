# Database Schema Documentation

## Overview
This document describes the database schema for the Expiry Tracker application. The schema is managed using SQLAlchemy ORM and Alembic for migrations.

## Core Tables

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP WITH TIME ZONE,
    security_question VARCHAR(255),
    security_answer_hash VARCHAR(128),
    two_factor_enabled BOOLEAN DEFAULT false,
    two_factor_secret VARCHAR(32),
    failed_login_attempts INTEGER DEFAULT 0,
    last_failed_login TIMESTAMP WITH TIME ZONE,
    account_locked_until TIMESTAMP WITH TIME ZONE
);
```

### Items Table
```sql
CREATE TABLE items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    expiry_date DATE NOT NULL,
    quantity INTEGER NOT NULL,
    status VARCHAR(20) NOT NULL,
    user_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    zoho_item_id VARCHAR(100),
    category_id INTEGER REFERENCES categories(id),
    location VARCHAR(255),
    batch_number VARCHAR(100),
    manufacturer VARCHAR(255),
    notes TEXT
);
```

### Notifications Table
```sql
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    item_id INTEGER REFERENCES items(id),
    message TEXT NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP WITH TIME ZONE
);
```

### Reports Table
```sql
CREATE TABLE reports (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    date DATE NOT NULL,
    report_type VARCHAR(50) NOT NULL,
    data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, date)
);
```

### Categories Table
```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

## Relationships

### User Relationships
- One-to-Many with Items (User -> Items)
- One-to-Many with Notifications (User -> Notifications)
- One-to-Many with Reports (User -> Reports)

### Item Relationships
- Many-to-One with User (Item -> User)
- Many-to-One with Category (Item -> Category)
- One-to-Many with Notifications (Item -> Notifications)

### Notification Relationships
- Many-to-One with User (Notification -> User)
- Many-to-One with Item (Notification -> Item)

### Report Relationships
- Many-to-One with User (Report -> User)

## Indexes

### Users Table
- Primary Key: `id`
- Unique: `username`, `email`

### Items Table
- Primary Key: `id`
- Foreign Key: `user_id`, `category_id`
- Index: `expiry_date`, `status`

### Notifications Table
- Primary Key: `id`
- Foreign Key: `user_id`, `item_id`
- Index: `status`, `created_at`

### Reports Table
- Primary Key: `id`
- Foreign Key: `user_id`
- Unique: `(user_id, date)`

### Categories Table
- Primary Key: `id`
- Unique: `name`

## Constraints

### Users Table
- `username` must be unique
- `email` must be unique
- `is_active` defaults to true
- `failed_login_attempts` defaults to 0

### Items Table
- `name` cannot be null
- `expiry_date` cannot be null
- `quantity` cannot be null
- `status` cannot be null
- `user_id` must reference a valid user

### Notifications Table
- `message` cannot be null
- `status` cannot be null
- `user_id` must reference a valid user
- `item_id` must reference a valid item

### Reports Table
- `date` cannot be null
- `report_type` cannot be null
- `data` cannot be null
- `user_id` must reference a valid user
- Combination of `user_id` and `date` must be unique

### Categories Table
- `name` cannot be null and must be unique

## Data Types

### Common Types
- `SERIAL`: Auto-incrementing integer
- `VARCHAR(n)`: Variable-length string with max length n
- `TEXT`: Unlimited length string
- `BOOLEAN`: True/false value
- `TIMESTAMP WITH TIME ZONE`: Date and time with timezone
- `DATE`: Date without time
- `INTEGER`: Whole number
- `JSONB`: Binary JSON data

## Security Features

### User Security
- Password hashing
- Security questions
- Two-factor authentication
- Login attempt tracking
- Account locking

### Data Protection
- Foreign key constraints
- Unique constraints
- Not null constraints
- Default values
- Cascading updates/deletes where appropriate

## Migration History
The database schema is managed using Alembic migrations. Key migrations include:
1. Initial migration
2. Add security fields
3. Fix users table
4. Add status column to notifications
5. Cleanup in-app notifications
6. Fix report date constraint

For detailed migration history, see [migrations/README.md](migrations/README.md). 