# Notifications Guide

The notification system keeps you informed about important inventory events, expiry dates, and system updates. This guide covers all aspects of managing and configuring notifications.

## Notification Types

### Email Notifications

**Daily Status Updates**
- Sent automatically at 9:11 PM BST
- Summary of items expiring within 30 days
- Current inventory status
- Risk assessment

**Expiry Alerts**
- Critical items shown in red (≤3 days)
- Items expiring within 7 days shown in yellow
- Future Expiries shown in gray

**System Notifications**
- Account verification emails
- Password reset confirmations

### In-App Notifications

**Real-Time Alerts**
- Instant notifications for critical events
- Daily notification updates

## Notification Settings

### Email Preferences

**Enable/Disable Notifications**
1. Go to **Settings** → **Notification Preferences**
2. Toggle **Email Notifications** on/off
3. **Password verification** required for changes
4. Save settings

**Alert Thresholds**
- **Critical**: ≤3 days to expiry
- **Warning**: 4-7 days to expiry
- **Notice**: 8-30 days to expiry

## Managing Notifications

### Viewing Notifications

**Notifications Page**
1. Click **Notifications** in navigation
2. View all notifications with filters:
   - **All**: Complete notification history
   - **Pending**: Unread notifications
   - **Sent**: Processed notifications

**Search Functionality**
- Search by notification message
- Date-based search

### Notification Actions

**Mark as Read**
- Click notification to mark as read
- Bulk mark multiple notifications
- Auto-mark after viewing

## Notification Schedule

### Daily Notifications

**Timing**
- **Send Time**: 9:11 PM BST (fixed)
- **Timezone**: Europe/London
- **Frequency**: Once per day

**Duplicate Prevention**
- System prevents duplicate notifications
- Only sends if not marked sent
- Respects user preferences

## Notification Templates

### Email Templates

**Daily Status Update**
```
Subject: Expiry Tracker - Daily Item Status Update

Dear [Username],

Here's your daily inventory status update:

Items Expiring Soon:
- [Item Name] expires in [X] days
- [Item Name] expires in [X] days

Total Inventory Value: £[Amount]
Items at Risk: [Count]
Risk Score: [Score]/100

View full report: [Link]

Best regards,
Expiry Tracker Team
```

## Notification Troubleshooting

### Common Issues

**Not Receiving Emails**
1. **Check Spam Folder**
   - Add sender to contacts
   - Mark as "Not Spam"
   - Check email filters

2. **Verify Settings**
   - Email notifications enabled
   - Correct email address
   - Valid email configuration

3. **Check Email Service**
   - Gmail app password setup
   - SMTP configuration
   - Service status

**Duplicate Notifications**
1. **Check Notification Settings**
   - Verify frequency settings
   - Review alert thresholds
   - Check timezone settings

2. **System Configuration**
   - WERKZEUG_RUN_MAIN setting
   - Scheduler configuration
   - Database consistency

**Wrong Timing**
1. **Timezone Settings**
   - Verify timezone configuration
   - Check daylight saving time
   - Update system time

2. **Scheduler Settings**
   - Review cron job timing
   - Check server timezone
   - Verify notification schedule

### Performance Issues

**Slow Notification Delivery**
- Check email service performance
- Review system resources
- Optimize database queries
- Monitor network connectivity

**High Email Volume**
- Adjust notification frequency
- Implement rate limiting
- Use bulk email services
- Optimize template delivery

## Best Practices

### Notification Management

1. **Regular Review**
   - Check notifications daily
   - Review notification settings
   - Clean up old notifications
   - Monitor notification effectiveness

2. **Optimization**
   - Set appropriate thresholds
   - Avoid notification fatigue
   - Balance frequency and importance

3. **Security**
   - Verify email addresses
   - Use secure email services

---

**Previous**: [Dashboard Overview](./dashboard.md) | **Next**: [Reports](./reports.md) 