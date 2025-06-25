# Database Backup System

This directory contains a comprehensive database backup and restore system for the Expiry Tracker application.

## Overview

The backup system provides:
- **Automated database backups** with compression and rotation
- **Safe restore operations** with validation and rollback capabilities
- **Scheduled backups** using cron jobs
- **Configuration management** for backup settings
- **Logging and monitoring** of backup operations

## Files

### Core Scripts

- **`backup_db.py`** - Main backup script with comprehensive features
- **`backup_restore.py`** - Safe restore script with validation
- **`backup_scheduler.py`** - Automated backup scheduling
- **`backup_config.json`** - Default backup configuration

### Configuration

- **`backup_config.json`** - Backup settings and options
- **`BACKUP_README.md`** - This documentation file

## Quick Start

### 1. Create a Backup

```bash
# Create a backup now
python scripts/backup_db.py

# Create backup with verbose output
python scripts/backup_db.py --verbose
```

### 2. List Available Backups

```bash
# List all backups
python scripts/backup_db.py --list-backups

# Or use the restore script
python scripts/backup_restore.py --list-backups
```

### 3. Restore from Backup

```bash
# Restore with safety checks
python scripts/backup_restore.py backup_file.backup.gz

# Dry run (validate without restoring)
python scripts/backup_restore.py --dry-run backup_file.backup.gz

# Force restore (skip confirmations)
python scripts/backup_restore.py --force backup_file.backup.gz
```

### 4. Set Up Automated Backups

```bash
# Install daily cron job (runs at 2:00 AM)
python scripts/backup_scheduler.py --install-cron

# Install weekly cron job
python scripts/backup_scheduler.py --install-cron --frequency weekly

# Install monthly cron job at specific time
python scripts/backup_scheduler.py --install-cron --frequency monthly --time 03:00

# Check cron job status
python scripts/backup_scheduler.py --status

# Remove cron job
python scripts/backup_scheduler.py --remove-cron
```

## Configuration

### Backup Configuration (`backup_config.json`)

```json
{
  "backup_retention_days": 30,
  "compression": true,
  "include_schema": true,
  "include_data": true,
  "backup_format": "custom",
  "pg_dump_options": [
    "--verbose",
    "--no-owner",
    "--no-privileges"
  ],
  "notification_email": null,
  "backup_schedule": {
    "enabled": false,
    "frequency": "daily",
    "time": "02:00"
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `backup_retention_days` | int | 30 | Days to keep backups before cleanup |
| `compression` | bool | true | Enable gzip compression |
| `include_schema` | bool | true | Include database schema |
| `include_data` | bool | true | Include data |
| `backup_format` | string | "custom" | Format: custom, plain, directory |
| `pg_dump_options` | array | [] | Additional pg_dump options |
| `notification_email` | string | null | Email for backup notifications |

## Backup Formats

### Custom Format (Recommended)
- **Extension**: `.backup`
- **Compressed**: `.backup.gz`
- **Features**: Binary format, fastest restore, includes all metadata

### Plain SQL
- **Extension**: `.sql`
- **Compressed**: `.sql.gz`
- **Features**: Human-readable, portable, slower restore

### Directory Format
- **Extension**: `.dir`
- **Features**: Directory structure, parallel restore, largest size

## Safety Features

### Pre-Restore Backups
- Automatically creates a backup before any restore operation
- Provides rollback capability if restore fails
- Files named: `pre_restore_backup_YYYYMMDD_HHMMSS.backup.gz`

### Validation
- File integrity checks
- Size validation
- Compression testing
- Format verification

### Confirmation Prompts
- Requires explicit confirmation for destructive operations
- Shows detailed information before restore
- Can be bypassed with `--force` flag

## File Locations

### Backup Storage
- **Directory**: `database_backups/`
- **Pattern**: `expiry_tracker_backup_YYYYMMDD_HHMMSS.backup.gz`
- **Excluded from Git**: All backup files are in `.gitignore`

### Logs
- **Backup logs**: `logs/backup_scheduler.log`
- **Cron logs**: `logs/cron_backup.log`
- **Application logs**: `logs/` (general application logs)

### Configuration
- **Main config**: `backup_config.json`
- **Git ignored**: Configuration files are excluded from version control

## Cron Job Management

### Installing Cron Jobs

The scheduler can automatically install cron jobs for different frequencies:

```bash
# Daily at 2:00 AM
python scripts/backup_scheduler.py --install-cron

# Weekly on Sunday at 2:00 AM
python scripts/backup_scheduler.py --install-cron --frequency weekly

# Monthly on 1st at 3:00 AM
python scripts/backup_scheduler.py --install-cron --frequency monthly --time 03:00
```

### Cron Job Details

- **User**: Runs as current user
- **Logging**: Output goes to `logs/cron_backup.log`
- **Timeout**: 2-hour maximum runtime
- **Error handling**: Failed backups are logged

### Manual Cron Management

You can also manage cron jobs manually:

```bash
# View current cron jobs
crontab -l

# Edit cron jobs
crontab -e

# Remove all cron jobs
crontab -r
```

## Troubleshooting

### Common Issues

#### 1. Permission Denied
```bash
# Make scripts executable
chmod +x scripts/backup_db.py
chmod +x scripts/backup_restore.py
chmod +x scripts/backup_scheduler.py
```

#### 2. Database Connection Failed
- Check `DATABASE_URL` environment variable
- Verify PostgreSQL is running
- Check network connectivity
- Validate credentials

#### 3. Insufficient Disk Space
- Check available space: `df -h`
- Clean old backups: `python scripts/backup_db.py --cleanup`
- Adjust retention policy in config

#### 4. Cron Job Not Running
- Check cron service: `sudo systemctl status cron`
- Verify cron job exists: `crontab -l`
- Check logs: `tail -f logs/cron_backup.log`

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
# Verbose backup
python scripts/backup_db.py --verbose

# Verbose restore
python scripts/backup_restore.py --verbose backup_file.backup.gz
```

### Log Analysis

```bash
# View recent backup logs
tail -f logs/backup_scheduler.log

# Search for errors
grep -i error logs/backup_scheduler.log

# Check cron execution
grep -i cron logs/cron_backup.log
```

## Best Practices

### 1. Regular Testing
- Test restore operations in a development environment
- Verify backup integrity regularly
- Monitor backup sizes and completion times

### 2. Storage Management
- Monitor disk space usage
- Implement backup rotation
- Consider off-site storage for critical data

### 3. Security
- Secure backup files with appropriate permissions
- Encrypt sensitive backup data
- Use secure transfer methods for off-site backups

### 4. Monitoring
- Set up alerts for backup failures
- Monitor backup completion times
- Track backup sizes for anomalies

## Integration with Application

### Environment Variables
The backup system uses the same database configuration as the main application:

```bash
# Set database URL
export DATABASE_URL="postgresql://user:pass@localhost/dbname"

# Or use Flask app configuration
# The scripts will automatically detect Flask app settings
```

### Application Integration
- Backups don't interfere with application operation
- Can run while application is active
- Uses same database connection settings
- Logs are integrated with application logging

## Migration and Deployment

### New Installation
1. Copy backup scripts to `scripts/` directory
2. Create `database_backups/` directory
3. Configure `backup_config.json`
4. Test backup and restore operations
5. Set up automated scheduling

### Existing Installation
1. Backup current database manually
2. Update backup scripts
3. Test new backup system
4. Migrate to automated backups

### Production Deployment
1. Set up dedicated backup storage
2. Configure monitoring and alerts
3. Test disaster recovery procedures
4. Document backup procedures
5. Train team on restore operations

## Support

For issues with the backup system:

1. Check the troubleshooting section above
2. Review logs in `logs/` directory
3. Test with verbose mode enabled
4. Verify database connectivity
5. Check system resources (disk space, memory)

The backup system is designed to be robust and self-documenting. Most issues can be resolved by checking the logs and following the troubleshooting steps. 