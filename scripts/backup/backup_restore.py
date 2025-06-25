#!/usr/bin/env python3
"""
Database Restore Script for Expiry Tracker

This script provides a safe way to restore database backups with
validation, confirmation prompts, and rollback capabilities.

Usage:
    python scripts/backup_restore.py <backup_file>
    python scripts/backup_restore.py --list-backups
    python scripts/backup_restore.py --dry-run <backup_file>
"""

import os
import sys
import subprocess
import argparse
import logging
import gzip
import shutil
import tempfile
from pathlib import Path
from datetime import datetime
import json
import getpass
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseRestore:
    """Handles database restore operations with safety features."""
    
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.backup_dir = app_root / "database_backups"
        self.temp_dir = app_root / "temp_restore"
        
    def get_database_url(self) -> Optional[str]:
        """Get database URL from environment or config."""
        # Try environment variable first
        db_url = os.environ.get('DATABASE_URL')
        if db_url:
            return db_url
        
        # Try to get from Flask app
        try:
            sys.path.insert(0, str(self.app_root))
            from app import create_app
            from app.core.extensions import db
            
            app = create_app('development')
            with app.app_context():
                return str(db.engine.url)
        except Exception as e:
            logger.error(f"Failed to get database URL from app: {e}")
            return None
    
    def parse_database_url(self, db_url: str) -> dict:
        """Parse database URL into components."""
        try:
            # Remove postgresql:// prefix
            if db_url.startswith('postgresql://'):
                db_url = db_url[13:]
            
            # Split into parts
            if '@' in db_url:
                auth_part, rest = db_url.split('@', 1)
                if ':' in auth_part:
                    username, password = auth_part.split(':', 1)
                else:
                    username, password = auth_part, ''
                
                if ':' in rest:
                    host_port, database = rest.rsplit('/', 1)
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                    else:
                        host, port = host_port, '5432'
                else:
                    host, port = rest, '5432'
                    database = ''
            else:
                # No authentication
                username = password = ''
                if ':' in db_url:
                    host_port, database = db_url.rsplit('/', 1)
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                    else:
                        host, port = host_port, '5432'
                else:
                    host, port = db_url, '5432'
                    database = ''
            
            return {
                'username': username,
                'password': password,
                'host': host,
                'port': port,
                'database': database
            }
        except Exception as e:
            logger.error(f"Failed to parse database URL: {e}")
            return {}
    
    def list_backups(self) -> list:
        """List all available backups."""
        try:
            if not self.backup_dir.exists():
                return []
            
            backups = []
            for backup_file in self.backup_dir.glob("expiry_tracker_backup_*"):
                stat = backup_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                
                # Parse timestamp from filename
                try:
                    timestamp_str = backup_file.stem.split('_')[-1]
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except:
                    timestamp = datetime.fromtimestamp(stat.st_mtime)
                
                backups.append({
                    'filename': backup_file.name,
                    'path': backup_file,
                    'size_mb': size_mb,
                    'created': timestamp,
                    'compressed': backup_file.suffix.endswith('.gz')
                })
            
            # Sort by creation date (newest first)
            backups.sort(key=lambda x: x['created'], reverse=True)
            return backups
            
        except Exception as e:
            logger.error(f"Failed to list backups: {e}")
            return []
    
    def validate_backup_file(self, backup_path: Path) -> bool:
        """Validate backup file integrity."""
        try:
            if not backup_path.exists():
                logger.error(f"Backup file not found: {backup_path}")
                return False
            
            # Check file size
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            if size_mb < 0.1:  # Less than 100KB
                logger.warning(f"Backup file seems too small: {size_mb:.2f} MB")
            
            # Check if compressed
            is_compressed = backup_path.suffix.endswith('.gz')
            
            # Test decompression if compressed
            if is_compressed:
                try:
                    with gzip.open(backup_path, 'rb') as f:
                        # Read first few bytes to test decompression
                        f.read(1024)
                    logger.info("Compressed backup file is valid")
                except Exception as e:
                    logger.error(f"Failed to decompress backup file: {e}")
                    return False
            
            # Check file format
            if backup_path.suffix in ['.backup', '.sql']:
                logger.info("Backup file format appears valid")
            else:
                logger.warning(f"Unknown backup file format: {backup_path.suffix}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to validate backup file: {e}")
            return False
    
    def create_backup_before_restore(self) -> Optional[Path]:
        """Create a backup of current database before restore."""
        try:
            logger.info("Creating backup of current database...")
            
            # Import backup script
            sys.path.insert(0, str(self.app_root / "scripts" / "backup"))
            from backup_db import DatabaseBackup
            
            backup_system = DatabaseBackup(self.app_root)
            config = backup_system.load_config()
            
            # Create backup with special name
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"pre_restore_backup_{timestamp}.backup"
            if config.get('compression', True):
                filename += '.gz'
            
            backup_path = self.backup_dir / filename
            
            # Create backup
            if backup_system.run_pg_dump(backup_system.parse_database_url(backup_system.get_database_url()), backup_path, config):
                logger.info(f"Pre-restore backup created: {backup_path}")
                return backup_path
            else:
                logger.error("Failed to create pre-restore backup")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create pre-restore backup: {e}")
            return None
    
    def restore_backup(self, backup_path: Path, dry_run: bool = False, force: bool = False) -> bool:
        """Restore database from backup with safety checks."""
        try:
            # Validate backup file
            if not self.validate_backup_file(backup_path):
                return False
            
            # Get database configuration
            db_url = self.get_database_url()
            if not db_url:
                logger.error("No database URL found")
                return False
            
            db_config = self.parse_database_url(db_url)
            if not db_config:
                logger.error("Failed to parse database URL")
                return False
            
            # Show restore information
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info(f"Restore Information:")
            logger.info(f"  Backup file: {backup_path}")
            logger.info(f"  Size: {size_mb:.2f} MB")
            logger.info(f"  Database: {db_config.get('database', 'N/A')}")
            logger.info(f"  Host: {db_config.get('host', 'N/A')}")
            
            if dry_run:
                logger.info("DRY RUN: No actual restore will be performed")
                return True
            
            # Create pre-restore backup
            pre_restore_backup = self.create_backup_before_restore()
            if not pre_restore_backup:
                if not force:
                    logger.error("Failed to create pre-restore backup. Use --force to continue anyway.")
                    return False
                else:
                    logger.warning("Continuing without pre-restore backup (--force specified)")
            
            # Confirmation prompt
            if not force:
                print("\n⚠️  WARNING: This will overwrite your current database!")
                print(f"   Backup file: {backup_path}")
                print(f"   Database: {db_config.get('database', 'N/A')}")
                print(f"   Host: {db_config.get('host', 'N/A')}")
                
                if pre_restore_backup:
                    print(f"   Pre-restore backup: {pre_restore_backup}")
                
                confirm = input("\nType 'RESTORE' to confirm: ")
                if confirm != 'RESTORE':
                    logger.info("Restore cancelled by user")
                    return False
            
            # Prepare restore command
            cmd = ['pg_restore']
            
            # Add connection parameters
            if db_config.get('host'):
                cmd.extend(['-h', db_config['host']])
            if db_config.get('port'):
                cmd.extend(['-p', db_config['port']])
            if db_config.get('username'):
                cmd.extend(['-U', db_config['username']])
            if db_config.get('database'):
                cmd.extend(['-d', db_config['database']])
            
            # Add restore options
            cmd.extend([
                '--clean',           # Drop database objects before recreating
                '--if-exists',       # Don't error if objects don't exist
                '--verbose',         # Show progress
                '--no-owner',        # Don't set ownership
                '--no-privileges'    # Don't restore privileges
            ])
            
            # Add input file
            cmd.append(str(backup_path))
            
            # Set password environment variable
            env = os.environ.copy()
            if db_config.get('password'):
                env['PGPASSWORD'] = db_config['password']
            
            logger.info("Starting database restore...")
            logger.info(f"Command: {' '.join(cmd[:5])}...")
            
            # Run restore
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=7200  # 2 hour timeout
            )
            
            if result.returncode == 0:
                logger.info("✅ Database restore completed successfully!")
                
                if pre_restore_backup:
                    logger.info(f"Pre-restore backup available at: {pre_restore_backup}")
                
                return True
            else:
                logger.error(f"❌ Database restore failed!")
                logger.error(f"Error output: {result.stderr}")
                
                if pre_restore_backup:
                    logger.info(f"You can restore from the pre-restore backup: {pre_restore_backup}")
                
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("❌ Database restore timed out after 2 hours")
            return False
        except Exception as e:
            logger.error(f"❌ Failed to restore database: {e}")
            return False

def main():
    """Main entry point for the restore script."""
    parser = argparse.ArgumentParser(
        description="Database restore utility with safety features",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/backup_restore.py backup_file.backup.gz
  python scripts/backup_restore.py --list-backups
  python scripts/backup_restore.py --dry-run backup_file.backup.gz
  python scripts/backup_restore.py --force backup_file.backup.gz
        """
    )
    
    parser.add_argument(
        'backup_file',
        nargs='?',
        help='Backup file to restore from'
    )
    
    parser.add_argument(
        '--list-backups',
        action='store_true',
        help='List all available backups'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate backup file without restoring'
    )
    
    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompts'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get application root (go up two levels from scripts/backup/)
    script_dir = Path(__file__).parent
    app_root = script_dir.parent.parent
    
    # Validate app root
    if not (app_root / "app").exists():
        logger.error("Invalid application root. Make sure you're running this from the project directory.")
        sys.exit(1)
    
    # Initialize restore system
    restore_system = DatabaseRestore(app_root)
    
    try:
        if args.list_backups:
            backups = restore_system.list_backups()
            if not backups:
                print("No backups found.")
                return 0
            
            print(f"Found {len(backups)} backup(s):")
            print("-" * 80)
            for backup in backups:
                print(f"File: {backup['filename']}")
                print(f"Size: {backup['size_mb']:.2f} MB")
                print(f"Created: {backup['created'].strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"Compressed: {backup['compressed']}")
                print("-" * 80)
            return 0
        
        elif not args.backup_file:
            parser.print_help()
            return 1
        
        else:
            # Resolve backup file path
            backup_path = Path(args.backup_file)
            if not backup_path.is_absolute():
                backup_path = restore_system.backup_dir / backup_path
            
            # Validate backup file
            if not restore_system.validate_backup_file(backup_path):
                print("❌ Invalid backup file!")
                return 1
            
            # Perform restore
            if restore_system.restore_backup(backup_path, args.dry_run, args.force):
                print("✅ Restore operation completed successfully!")
                return 0
            else:
                print("❌ Restore operation failed!")
                return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Restore operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Restore operation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 