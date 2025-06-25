# Logging Quick Reference

## Essential Commands

### Real-time Monitoring
```bash
# Monitor all logs
tail -f logs/*.log

# Monitor main application log
tail -f logs/app.log

# Monitor credential access
tail -f logs/credential_access.log

# Monitor errors only
tail -f logs/error.log
```

### Search and Filter
```bash
# Find all errors
grep -i "error" logs/app.log

# Find specific user activities
grep "User ID: 123" logs/app.log

# Find today's logs
grep "$(date '+%Y-%m-%d')" logs/app.log

# Find logs from last hour
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" logs/app.log

# Check HTTP status codes
grep "HTTP/1.1" logs/access.log | awk '{print $9}' | sort | uniq -c
```

### Performance Analysis
```bash
# Request count by endpoint
grep "HTTP/1.1" logs/access.log | awk '{print $7}' | sort | uniq -c | sort -n -r

# Most accessed endpoints
grep "HTTP/1.1" logs/access.log | awk '{print $7}' | sort | uniq -c | sort -n -r | head -10

# Error rate calculation
total=$(grep -c "HTTP/1.1" logs/access.log)
errors=$(grep "HTTP/1.1" logs/access.log | awk '$9 >= 400 {count++} END {print count}')
echo "Error rate: $(echo "scale=2; $errors * 100 / $total" | bc)%"
```

### User Activity Analysis
```bash
# Most active users
grep "User ID:" logs/app.log | grep -o "User ID: [0-9]*" | sort | uniq -c | sort -n -r

# User login/logout patterns
grep -E "login|logout" logs/access.log

# Credential access attempts
grep "credential" logs/credential_access.log
```

## Common Issues & Solutions

### Application Won't Start
```bash
# Check startup logs
tail -20 logs/app.log

# Look for configuration errors
grep -i "config\|environment" logs/app.log

# Check system-level errors
tail -20 logs/error.log
```

### Email Issues
```bash
# Check email service logs
grep -i "mail\|email\|smtp" logs/app.log

# Monitor notification delivery
grep -i "notification" logs/app.log
```

### Zoho Integration Issues
```bash
# Check credential logs
tail -20 logs/credential_access.log

# Look for Zoho errors
grep -i "zoho\|credential" logs/app.log
```

### Authentication Problems
```bash
# Check auth requests
grep "auth" logs/access.log

# Look for credential access issues
grep -i "credential\|verification" logs/credential_access.log
```

## Log Statistics

### System Health Check
```bash
# Log entry count by level
grep -o "INFO\|WARNING\|ERROR" logs/app.log | sort | uniq -c

# Error rate calculation
total=$(grep -c "INFO\|WARNING\|ERROR" logs/app.log)
errors=$(grep -c "ERROR" logs/app.log)
echo "Error rate: $(echo "scale=2; $errors * 100 / $total" | bc)%"

# Recent activity summary
echo "=== Last Hour Activity ==="
grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" logs/app.log | wc -l
echo "=== Today's Activity ==="
grep "$(date '+%Y-%m-%d')" logs/app.log | wc -l
```

### HTTP Request Analysis
```bash
# HTTP status code distribution
echo "=== HTTP Status Codes ==="
grep "HTTP/1.1" logs/access.log | awk '{print $9}' | sort | uniq -c

# Most requested endpoints
echo "=== Top Endpoints ==="
grep "HTTP/1.1" logs/access.log | awk '{print $7}' | sort | uniq -c | sort -n -r | head -10

# Request methods distribution
echo "=== Request Methods ==="
grep "HTTP/1.1" logs/access.log | awk '{print $6}' | sort | uniq -c
```

## Maintenance Commands

### Log Cleanup
```bash
# Check log file sizes
ls -lh logs/*.log

# Compress old logs
gzip logs/app.log.*

# Remove logs older than 30 days
find logs/ -name "*.log.*" -mtime +30 -delete

# Check disk usage
du -sh logs/
```

### Log Backup
```bash
# Create backup of current logs
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/

# Backup only today's logs
grep "$(date '+%Y-%m-%d')" logs/app.log > logs_backup_$(date +%Y%m%d).txt
```

## Monitoring Scripts

### Simple Health Check
```bash
#!/bin/bash
# health_check.sh

echo "=== System Health Check ==="
echo "Timestamp: $(date)"

# Check if logs are being written
if [ -f logs/app.log ]; then
    last_modified=$(stat -c %Y logs/app.log)
    current_time=$(date +%s)
    time_diff=$((current_time - last_modified))
    
    if [ $time_diff -gt 300 ]; then
        echo "WARNING: Logs not updated in last 5 minutes"
    else
        echo "OK: Logs are being updated"
    fi
else
    echo "ERROR: app.log not found"
fi

# Check error rate
recent_errors=$(grep "$(date '+%Y-%m-%d %H')" logs/app.log | grep -c "ERROR" || echo "0")
recent_total=$(grep "$(date '+%Y-%m-%d %H')" logs/app.log | wc -l || echo "0")

if [ $recent_total -gt 0 ]; then
    error_rate=$(echo "scale=2; $recent_errors * 100 / $recent_total" | bc)
    echo "Error rate this hour: ${error_rate}%"
else
    echo "No recent log entries"
fi
```

### HTTP Performance Monitor
```bash
#!/bin/bash
# http_performance_monitor.sh

echo "=== HTTP Performance Monitor ==="
echo "Timestamp: $(date)"

# Request count in last 100 entries
recent_requests=$(tail -100 logs/access.log | grep -c "HTTP/1.1")
echo "Recent requests (last 100): ${recent_requests}"

# Error count in last 100 entries
recent_errors=$(tail -100 logs/access.log | grep "HTTP/1.1" | awk '$9 >= 400' | wc -l)
echo "Recent errors (last 100): ${recent_errors}"

# Top endpoints in last 100 requests
echo "Top endpoints (last 100 requests):"
tail -100 logs/access.log | grep "HTTP/1.1" | awk '{print $7}' | sort | uniq -c | sort -n -r | head -5
```

## Environment-Specific Commands

### Development
```bash
# Monitor development logs
tail -f logs/app.log | grep -v "DEBUG"

# Check for development-specific issues
grep -i "development\|debug" logs/app.log
```

### Production
```bash
# Monitor production logs with alerting
tail -f logs/app.log | grep -E "(ERROR|CRITICAL)" | while read line; do
    echo "ALERT: $line" | mail -s "Production Alert" admin@example.com
done

# Check for high error rates
error_count=$(grep "$(date '+%Y-%m-%d %H')" logs/app.log | grep -c "ERROR")
if [ $error_count -gt 10 ]; then
    echo "WARNING: High error rate detected: $error_count errors this hour"
fi
```

### Testing
```bash
# Check test logs
grep -i "test" logs/app.log

# Monitor test execution
tail -f logs/app.log | grep -E "(test|TEST)"
```

## Quick Debugging

### Database Issues
```bash
# Check database connection errors
grep -i "database\|sql\|connection" logs/app.log

# Look for query performance issues
grep -i "query\|slow" logs/app.log
```

### Email Issues
```bash
# Check email sending errors
grep -i "mail\|email\|smtp" logs/app.log

# Monitor notification delivery
grep -i "notification" logs/app.log
```

### Scheduler Issues
```bash
# Check scheduler job status
grep -i "scheduler\|job\|cleanup" logs/app.log

# Monitor scheduled task execution
grep -i "task\|scheduled" logs/app.log
```

### Zoho Issues
```bash
# Check credential access
grep -i "credential\|zoho" logs/credential_access.log

# Monitor rate limiting
grep -i "rate limit" logs/credential_access.log
```

## Tips & Tricks

1. **Use aliases for common commands**:
   ```bash
   alias logtail='tail -f logs/app.log'
   alias logerror='grep -i "error" logs/app.log'
   alias logaccess='tail -f logs/access.log'
   alias logcred='tail -f logs/credential_access.log'
   ```

2. **Create log analysis functions**:
   ```bash
   logstats() {
       echo "=== Log Statistics ==="
       echo "Total entries: $(wc -l < logs/app.log)"
       echo "Errors: $(grep -c "ERROR" logs/app.log)"
       echo "Warnings: $(grep -c "WARNING" logs/app.log)"
   }
   
   httpreport() {
       echo "=== HTTP Report ==="
       echo "Total requests: $(grep -c "HTTP/1.1" logs/access.log)"
       echo "Success (2xx): $(grep "HTTP/1.1" logs/access.log | awk '$9 >= 200 && $9 < 300' | wc -l)"
       echo "Client errors (4xx): $(grep "HTTP/1.1" logs/access.log | awk '$9 >= 400 && $9 < 500' | wc -l)"
       echo "Server errors (5xx): $(grep "HTTP/1.1" logs/access.log | awk '$9 >= 500' | wc -l)"
   }
   ```

3. **Monitor specific time periods**:
   ```bash
   # Last 15 minutes
   grep "$(date -d '15 minutes ago' '+%Y-%m-%d %H:%M')" logs/app.log
   
   # Specific date range
   grep "2025-01-15" logs/app.log | grep "10:"
   ```

4. **Export logs for analysis**:
   ```bash
   # Export HTTP requests to CSV
   grep "HTTP/1.1" logs/access.log | awk '{print $1, $4, $6, $7, $9, $10}' > http_requests.csv
   
   # Export credential access to CSV
   grep "Credential accessed" logs/credential_access.log | awk '{print $1, $2, $3, $4, $5, $6, $7, $8}' > credential_access.csv
   ``` 