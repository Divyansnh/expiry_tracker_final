# Database Documentation

This directory contains documentation related to the Expiry Tracker application's database structure, schema, and operations.

## Contents

- `schema.md`: Detailed database schema documentation including tables, relationships, and constraints
- `migrations/`: Database migration history and procedures
- `models/`: SQLAlchemy model definitions and relationships

## Database Overview

The Expiry Tracker application uses a relational database with the following key components:

1. **Core Models**:
   - Users: Authentication and user management
   - Items: Inventory management
   - Notifications: User notifications
   - Reports: Inventory reports
   - Categories: Item categorization

2. **Key Features**:
   - User authentication and authorization
   - Inventory tracking with expiry dates
   - Notification system
   - Report generation
   - Zoho Inventory integration

3. **Database Operations**:
   - Automatic status updates for items
   - Notification management
   - Report generation
   - Data validation and constraints

## Documentation Structure

1. **Schema Documentation** (`schema.md`)
   - Table definitions
   - Column specifications
   - Relationships
   - Constraints
   - Indexes

2. **Migration Documentation** (`migrations/`)
   - Migration history
   - Upgrade/downgrade procedures
   - Version control

3. **Model Documentation** (`models/`)
   - SQLAlchemy model definitions
   - Relationship mappings
   - Custom methods
   - Validation rules

## Related Documentation

- [API Documentation](../api/README.md)
- [User Guide](../user/README.md)
- [Developer Guide](../developer/README.md) 