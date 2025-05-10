# Notification System Maintenance

## Overview
The notification system sends daily updates about items that are expiring soon. Notifications are sent at 3:45 PM BST daily.

## Configuration
The notification system is configured in `app/__init__.py`:
```python
scheduler.add_job(
    id='send_daily_notifications',
    func=send_daily_notifications_task,
    trigger='cron',
    hour=1,  # 3 PM BST
    minute=45,
    timezone='Europe/London',
    misfire_grace_time=43200,  # Allow job to run up to 12 hours late
    coalesce=True,  # Run missed jobs only once on startup
    max_instances=1,  # Allow only one instance to run at a time
    replace_existing=True  # Replace existing job if it exists
)
```

## Duplicate Prevention
The system includes multiple layers of protection against duplicate notifications:

1. **Scheduler Protection**:
   - Uses `WERKZEUG_RUN_MAIN` check to prevent double initialization
   - Ensures only one instance runs at a time
   - Prevents missed jobs from running multiple times

2. **Notification Check**:
   ```python
   # Check if notification already sent today
   today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
   existing_notification = Notification.query.filter(
       and_(
           Notification.user_id == user.id,
           Notification.created_at >= today_start,
           Notification.type == 'email',
           Notification.status == 'sent'
       )
   ).first()
   ```

3. **Cleanup Tools**:
   - `scripts/cleanup_duplicate_notifications.py`: Removes duplicate notifications
   - `scripts/check_recent_notifications.py`: Verifies notification status

## Monitoring
To monitor the notification system:

1. Check logs for scheduler initialization:
```
INFO:app:Checking scheduler initialization conditions...
INFO:app:Testing mode: False
INFO:app:WERKZEUG_RUN_MAIN: true
INFO:app:Process ID: <pid>
INFO:app:Initializing scheduler in child process...
```

2. Verify notifications:
```bash
python scripts/check_recent_notifications.py
```

## Troubleshooting
If you notice duplicate notifications:

1. Check the logs for multiple scheduler initializations
2. Verify the `WERKZEUG_RUN_MAIN` environment variable
3. Run the cleanup script:
```bash
python scripts/cleanup_duplicate_notifications.py
```

## Best Practices
1. Always use the cleanup script before making changes
2. Monitor logs for scheduler initialization
3. Verify notification status regularly
4. Keep the scheduler configuration in sync with documentation 