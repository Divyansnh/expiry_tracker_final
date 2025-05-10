# Database Queries

Common queries and optimizations for the Expiry Tracker database.

## Common Queries

### User Queries
```sql
-- Get user by email
SELECT * FROM users WHERE email = ?;

-- Get user's items
SELECT * FROM items WHERE user_id = ?;

-- Get user's notifications
SELECT * FROM notifications WHERE user_id = ?;
```

### Item Queries
```sql
-- Get expiring items
SELECT * FROM items 
WHERE expiry_date BETWEEN ? AND ? 
AND user_id = ?;

-- Get low stock items
SELECT * FROM items 
WHERE quantity < ? 
AND user_id = ?;

-- Get items by status
SELECT * FROM items 
WHERE status = ? 
AND user_id = ?;
```

### Report Queries
```sql
-- Get daily report
SELECT * FROM reports 
WHERE date = ? 
AND user_id = ?;

-- Get report range
SELECT * FROM reports 
WHERE date BETWEEN ? AND ? 
AND user_id = ?;
```

## Query Optimization

### Index Usage
- Use appropriate indexes
- Avoid full table scans
- Optimize join operations
- Use covering indexes

### Performance Tips
- Limit result sets
- Use pagination
- Cache frequent queries
- Optimize joins

### Common Optimizations
```sql
-- Add index for frequent queries
CREATE INDEX idx_items_expiry ON items(expiry_date);

-- Use partial indexes
CREATE INDEX idx_active_users ON users(id) WHERE is_active = true;

-- Optimize joins
SELECT i.* FROM items i
JOIN users u ON i.user_id = u.id
WHERE u.email = ?;
```

## Best Practices

### Query Design
- Use prepared statements
- Avoid SELECT *
- Use appropriate data types
- Normalize data

### Performance
- Monitor query performance
- Use EXPLAIN ANALYZE
- Optimize indexes
- Cache results

### Security
- Use parameterized queries
- Validate input
- Limit permissions
- Audit queries 