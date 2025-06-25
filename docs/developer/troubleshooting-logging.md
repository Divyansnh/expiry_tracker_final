# Troubleshooting & Logging Guide

## Overview

This guide provides comprehensive information about the logging system in the Expiry Tracker application, designed to help developers and system administrators troubleshoot issues, monitor system health, and understand user activities.

## Logging Architecture

### Log Files Structure

The application maintains several specialized log files in the `logs/` directory:

```
logs/
├── app.log                    # Main application logs (rotating)
├── app.log.1, app.log.2, ...  # Rotated log files (up to 10 backups)
├── credential_access.log      # Zoho credential access logs
├── error.log                  # Error-specific logs (Gunicorn/WSGI)
├── access.log                 # HTTP access logs (standard format)
└── output.log                 # General output logs (empty)
```

### Log Rotation Configuration

- **Max File Size**: 10KB per log file
- **Backup Count**: 10 rotated files
- **Format**: `%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]`

## Log Categories

### 1. Application Logs (`app.log`)

**Purpose**: General application events, startup, configuration, and system operations.

**Key Events Logged**:
- Application startup and configuration
- Mail server configuration (non-sensitive)
- Scheduler initialization
- Email service operations
- Notification service activities

**Example Log Entries**:
```
2025-05-16 09:24:25,648 INFO: Expiry Tracker startup
2025-05-16 09:24:25,648 INFO: Mail server configuration:
2025-05-16 09:24:25,648 INFO: MAIL_SERVER: smtp.gmail.com
2025-05-16 09:24:25,698 INFO: Scheduler initialized with SQLAlchemy job store
2025-05-16 08:12:26,052 INFO: Email sent successfully to ['divyanshsingh1800@gmail.com']
```

### 2. Credential Access Logs (`credential_access.log`)

**Purpose**: Audit trail for Zoho credential access and management.

**Events Logged**:
- Credential access attempts
- Verification attempts (successful and failed)
- Rate limiting violations
- Security conflicts
- Email verification code operations

**Example Log Entries**:
```
2025-06-23 14:34:04,031 WARNING: Credential access attempt for user without credentials - User ID: 2, IP: 127.0.0.1
2025-06-23 14:39:57,840 INFO: Credential accessed - User ID: 2, IP: 127.0.0.1, Credential Type: zoho_client_secret, Timestamp: 2025-06-23 13:39:57.840162
2025-06-23 11:50:25,529 WARNING: Rate limit exceeded for enhanced disconnect verification - User ID: 2, IP: 127.0.0.1
```

### 3. HTTP Access Logs (`access.log`)

**Purpose**: Standard HTTP request logging in Common Log Format.

**Information Logged**:
- IP address
- Timestamp
- HTTP method and path
- Status code
- Response size
- User agent

**Example Log Entries**:
```
127.0.0.1 - - [17/Apr/2025:10:04:28 +0100] "GET /dashboard HTTP/1.1" 200 18982
127.0.0.1 - - [17/Apr/2025:10:04:33 +0100] "POST /auth/login HTTP/1.1" 302 189
127.0.0.1 - - [17/Apr/2025:10:14:26 +0100] "DELETE /delete_item/118 HTTP/1.1" 200 64
```

### 4. Error Logs (`error.log`)

**Purpose**: System-level errors and WSGI/Gunicorn errors.

**Events Logged**:
- Gunicorn startup errors
- Port conflicts
- Permission issues
- System-level failures

**Example Log Entries**:
```
[2025-04-17 10:00:01 +0100] [63382] [ERROR] Connection in use: ('0.0.0.0', 5000)
[2025-04-17 10:00:01 +0100] [63382] [ERROR] Retrying in 1 second.
```

### 5. User Activity Logs (Database)

**Purpose**: Comprehensive user activity tracking stored in the database.

**Activity Types**:
- `item_added` - New items created
- `item_updated` - Item modifications
- `item_deleted` - Item deletions
- `expiry_alert` - Expiry notifications
- `notification_sent` - Email notifications
- `report_generated` - Report creation
- `settings_updated` - Configuration changes
- `zoho_sync` - Zoho synchronization
- `login` - User login events
- `logout` - User logout events

**Data Structure**:
```json
{
  "id": 123,
  "user_id": 456,
  "activity_type": "item_added",
  "title": "New Item Added",
  "description": "Added item 'Product XYZ' with expiry date 2024-03-15",
  "activity_data": {
    "item_id": 789,
    "item_name": "Product XYZ",
    "expiry_date": "2024-03-15"
  },
  "created_at": "2024-01-15T10:30:00Z",
  "time_ago": "2 hours ago"
}
```

## Logging Configuration

### Environment-Specific Settings

#### Development
```python
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEBUG = True
```

#### Production
```python
LOG_LEVEL = 'INFO'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
DEBUG = False
```

#### Testing
```python
LOG_LEVEL = 'WARNING'  # Reduced logging for tests
TESTING = True
```

### Logger Configuration

```python
# Main application logger
app.logger.setLevel(logging.INFO)

# Credential access logger
credential_logger = logging.getLogger('credential_access')
credential_logger.setLevel(logging.INFO)

# Service-specific loggers
logger = logging.getLogger(__name__)  # Used in services
```

## Troubleshooting Common Issues

### 1. Application Startup Issues

**Symptoms**: Application fails to start or crashes immediately.

**Check These Logs**:
```bash
# Check main application logs
tail -f logs/app.log

# Look for startup errors
grep -i "error\|exception\|failed" logs/app.log

# Check system-level errors
tail -f logs/error.log
```

**Common Issues**:
- Database connection failures
- Missing environment variables
- Port conflicts
- Permission issues with log directory

**Debugging Steps**:
1. Verify environment variables are set
2. Check database connectivity
3. Ensure log directory permissions
4. Review configuration settings

### 2. Scheduler Job Issues

**Symptoms**: Scheduled tasks not running or failing.

**Check These Logs**:
```bash
# Check scheduler initialization
grep -i "scheduler\|job" logs/app.log

# Look for job execution errors
grep -i "cleanup\|notification" logs/app.log
```

**Common Issues**:
- Timezone configuration problems
- Job conflicts
- Database connection issues during job execution

**Debugging Steps**:
1. Verify timezone settings
2. Check job configuration
3. Review database connectivity
4. Monitor job execution times

### 3. Zoho Integration Issues

**Symptoms**: Zoho sync failures, credential problems.

**Check These Logs**:
```bash
# Check credential access logs
tail -f logs/credential_access.log

# Look for Zoho-related errors
grep -i "zoho\|credential" logs/app.log
```

**Common Issues**:
- Invalid credentials
- Rate limiting
- Network connectivity
- Token expiration

**Debugging Steps**:
1. Verify Zoho credentials
2. Check rate limiting status
3. Test network connectivity
4. Review token refresh logic

### 4. Email Issues

**Symptoms**: Email notifications not being sent.

**Check These Logs**:
```bash
# Check email service logs
grep -i "mail\|email\|smtp" logs/app.log

# Monitor notification delivery
grep -i "notification" logs/app.log
```

**Common Issues**:
- SMTP configuration problems
- Authentication failures
- Network connectivity
- Template rendering errors

**Debugging Steps**:
1. Verify SMTP settings
2. Check email credentials
3. Test network connectivity
4. Review email templates

### 5. Authentication Issues

**Symptoms**: Login failures, session problems.

**Check These Logs**:
```bash
# Check authentication requests
grep "auth" logs/access.log

# Look for credential access issues
grep -i "credential\|verification" logs/credential_access.log
```

**Common Issues**:
- Invalid credentials
- Session expiration
- Rate limiting
- CSRF token problems

**Debugging Steps**:
1. Verify user credentials
2. Check session configuration
3. Review CSRF settings
4. Monitor rate limiting

## Log Analysis Tools

### Built-in Analysis
- **Log Level Filtering**: Filter by DEBUG, INFO, WARNING, ERROR
- **Date Range Filtering**: Filter logs by date ranges
- **User Activity Tracking**: Monitor user actions and system events
- **Error Pattern Recognition**: Identify recurring issues

### External Tools
- **grep**: Search for specific patterns
- **awk**: Process and analyze log data
- **sed**: Stream editor for log manipulation
- **logrotate**: Automatic log rotation and compression

## Security and Privacy

### Sensitive Data Protection

**What's NOT Logged**:
- Passwords and authentication tokens
- Zoho credentials (only hashes logged)
- Personal user information
- API keys and secrets

**What's Masked**:
- Auth-related URLs in credential logs
- Sensitive configuration values
- Personal data in activity logs

### Audit Trail

**Comprehensive Tracking**:
- All user activities (database)
- Credential access attempts
- Security events
- System configuration changes

**Retention Policy**:
- Application logs: 10 rotated files (approximately 100KB)
- Credential logs: Persistent storage
- Activity logs: Database storage with cleanup
- Access logs: Standard web server format

## Best Practices

### 1. Log Monitoring

- Set up automated log monitoring
- Configure alerts for critical errors
- Regular log rotation and cleanup
- Backup important log data

### 2. Performance Optimization

- Use appropriate log levels
- Avoid logging in tight loops
- Implement structured logging
- Monitor log file sizes

### 3. Security Considerations

- Never log sensitive information
- Implement proper access controls
- Regular security audits
- Monitor for suspicious activities

### 4. Maintenance

- Regular log analysis
- Cleanup old log files
- Monitor disk space usage
- Update logging configuration as needed

## Integration with Monitoring Tools

### 1. Log Aggregation

Consider integrating with tools like:
- ELK Stack (Elasticsearch, Logstash, Kibana)
- Splunk
- Graylog
- Fluentd

### 2. Alerting

Set up alerts for:
- High error rates
- Performance degradation
- Security events
- System failures

### 3. Dashboards

Create dashboards for:
- System health monitoring
- User activity tracking
- Performance metrics
- Security events

## Conclusion

This comprehensive logging system provides excellent visibility into application behavior, user activities, and system health. By following this guide, you can effectively troubleshoot issues, monitor performance, and maintain system security.

For additional support or questions about the logging system, refer to the main documentation or contact the development team. 