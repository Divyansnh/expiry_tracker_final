#!/usr/bin/env python3
"""
Backup Scheduler for Expiry Tracker

This script can be used to schedule automated database backups.
It can be run manually or configured with cron/systemd.

Usage:
    python scripts/backup_scheduler.py
    python scripts/backup_scheduler.py --install-cron
    python scripts/backup_scheduler.py --remove-cron
"""

import os
import sys
import subprocess
import argparse
import logging
from pathlib import Path
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/backup_scheduler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BackupScheduler:
    """Handles automated backup scheduling."""
    
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.backup_script = app_root / "scripts" / "backup_db.py"
        self.config_file = app_root / "backup_config.json"
        self.logs_dir = app_root / "logs"
        
    def load_config(self):
        """Load backup configuration."""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}
    
    def run_backup(self):
        """Run the backup process."""
        try:
            logger.info("Starting scheduled backup...")
            
            # Change to app directory
            os.chdir(self.app_root)
            
            # Run backup script
            result = subprocess.run(
                [sys.executable, str(self.backup_script)],
                capture_output=True,
                text=True,
                timeout=7200  # 2 hour timeout
            )
            
            if result.returncode == 0:
                logger.info("Scheduled backup completed successfully")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Backup timed out after 2 hours")
            return False
        except Exception as e:
            logger.error(f"Failed to run backup: {e}")
            return False
    
    def install_cron_job(self, frequency: str = "daily", time: str = "02:00"):
        """Install cron job for automated backups."""
        try:
            # Get current user
            user = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()
            
            # Create cron command
            script_path = self.backup_script.absolute()
            log_file = self.logs_dir / "cron_backup.log"
            
            if frequency == "daily":
                hour, minute = time.split(":")
                cron_schedule = f"{minute} {hour} * * *"
            elif frequency == "weekly":
                hour, minute = time.split(":")
                cron_schedule = f"{minute} {hour} * * 0"  # Sunday
            elif frequency == "monthly":
                hour, minute = time.split(":")
                cron_schedule = f"{minute} {hour} 1 * *"  # 1st of month
            else:
                logger.error(f"Unsupported frequency: {frequency}")
                return False
            
            cron_command = f"{cron_schedule} {sys.executable} {script_path} >> {log_file} 2>&1"
            
            # Create temporary crontab
            temp_crontab = f"/tmp/crontab_{user}_backup"
            
            # Get current crontab
            current_crontab = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            ).stdout
            
            # Check if backup job already exists
            if "backup_db.py" in current_crontab:
                logger.warning("Backup cron job already exists")
                return True
            
            # Add new job
            new_crontab = current_crontab + f"\n# Expiry Tracker Database Backup\n{cron_command}\n"
            
            # Write to temporary file
            with open(temp_crontab, 'w') as f:
                f.write(new_crontab)
            
            # Install new crontab
            result = subprocess.run(['crontab', temp_crontab])
            
            # Clean up
            os.unlink(temp_crontab)
            
            if result.returncode == 0:
                logger.info(f"Backup cron job installed successfully ({frequency} at {time})")
                return True
            else:
                logger.error("Failed to install cron job")
                return False
                
        except Exception as e:
            logger.error(f"Failed to install cron job: {e}")
            return False
    
    def remove_cron_job(self):
        """Remove backup cron job."""
        try:
            # Get current crontab
            current_crontab = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            ).stdout
            
            # Remove backup-related lines
            lines = current_crontab.split('\n')
            filtered_lines = []
            
            skip_next = False
            for line in lines:
                if "backup_db.py" in line or "Expiry Tracker Database Backup" in line:
                    skip_next = True
                    continue
                if skip_next and line.strip() == "":
                    skip_next = False
                    continue
                if not skip_next:
                    filtered_lines.append(line)
            
            # Create temporary crontab
            user = subprocess.run(['whoami'], capture_output=True, text=True).stdout.strip()
            temp_crontab = f"/tmp/crontab_{user}_backup"
            
            with open(temp_crontab, 'w') as f:
                f.write('\n'.join(filtered_lines))
            
            # Install updated crontab
            result = subprocess.run(['crontab', temp_crontab])
            
            # Clean up
            os.unlink(temp_crontab)
            
            if result.returncode == 0:
                logger.info("Backup cron job removed successfully")
                return True
            else:
                logger.error("Failed to remove cron job")
                return False
                
        except Exception as e:
            logger.error(f"Failed to remove cron job: {e}")
            return False
    
    def show_cron_status(self):
        """Show current cron job status."""
        try:
            current_crontab = subprocess.run(
                ['crontab', '-l'],
                capture_output=True,
                text=True
            ).stdout
            
            if "backup_db.py" in current_crontab:
                print("✅ Backup cron job is installed")
                for line in current_crontab.split('\n'):
                    if "backup_db.py" in line:
                        print(f"   Schedule: {line}")
            else:
                print("❌ No backup cron job found")
                
        except Exception as e:
            logger.error(f"Failed to check cron status: {e}")

def main():
    """Main entry point for the backup scheduler."""
    parser = argparse.ArgumentParser(
        description="Backup scheduler for automated database backups",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/backup_scheduler.py              # Run backup now
  python scripts/backup_scheduler.py --install-cron # Install daily cron job
  python scripts/backup_scheduler.py --remove-cron  # Remove cron job
  python scripts/backup_scheduler.py --status      # Show cron status
        """
    )
    
    parser.add_argument(
        '--install-cron',
        action='store_true',
        help='Install cron job for automated backups'
    )
    
    parser.add_argument(
        '--remove-cron',
        action='store_true',
        help='Remove backup cron job'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current cron job status'
    )
    
    parser.add_argument(
        '--frequency',
        choices=['daily', 'weekly', 'monthly'],
        default='daily',
        help='Backup frequency (default: daily)'
    )
    
    parser.add_argument(
        '--time',
        default='02:00',
        help='Backup time in HH:MM format (default: 02:00)'
    )
    
    args = parser.parse_args()
    
    # Get application root
    script_dir = Path(__file__).parent
    app_root = script_dir.parent
    
    # Validate app root
    if not (app_root / "app").exists():
        logger.error("Invalid application root. Make sure you're running this from the project directory.")
        sys.exit(1)
    
    # Initialize scheduler
    scheduler = BackupScheduler(app_root)
    
    try:
        if args.install_cron:
            if scheduler.install_cron_job(args.frequency, args.time):
                print("✅ Cron job installed successfully!")
                return 0
            else:
                print("❌ Failed to install cron job!")
                return 1
        
        elif args.remove_cron:
            if scheduler.remove_cron_job():
                print("✅ Cron job removed successfully!")
                return 0
            else:
                print("❌ Failed to remove cron job!")
                return 1
        
        elif args.status:
            scheduler.show_cron_status()
            return 0
        
        else:
            # Run backup
            print("🚀 Running scheduled backup...")
            if scheduler.run_backup():
                print("✅ Backup completed successfully!")
                return 0
            else:
                print("❌ Backup failed!")
                return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Backup operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Backup operation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 