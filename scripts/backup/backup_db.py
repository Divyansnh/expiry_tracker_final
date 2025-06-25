#!/usr/bin/env python3
"""
Database Backup Script for Expiry Tracker

This script creates complete backups of your PostgreSQL database with proper
error handling, compression, and rotation of old backups.

Usage:
    python scripts/backup/backup_db.py
    python scripts/backup/backup_db.py --config-only
    python scripts/backup/backup_db.py --list-backups
    python scripts/backup/backup_db.py --cleanup
"""

import os
import sys
import subprocess
import argparse
import logging
import gzip
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DatabaseBackup:
    """Handles database backup operations."""
    
    def __init__(self, app_root: Path):
        self.app_root = app_root
        self.backup_dir = app_root / "database_backups"
        self.config_file = app_root / "scripts" / "backup" / "backup_config.json"
        self.default_config = {
            "backup_retention_days": 30,
            "compression": True,
            "include_schema": True,
            "include_data": True,
            "backup_format": "custom",  # custom, plain, directory
            "pg_dump_options": [],
            "notification_email": None
        }
        
    def load_config(self) -> Dict[str, Any]:
        """Load backup configuration."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                logger.info("Loaded backup configuration")
                return {**self.default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config, using defaults: {e}")
                return self.default_config
        else:
            logger.info("No config file found, using defaults")
            return self.default_config
    
    def save_config(self, config: Dict[str, Any]):
        """Save backup configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info("Backup configuration saved")
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
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
    
    def parse_database_url(self, db_url: str) -> Dict[str, str]:
        """Parse database URL into components."""
        try:
            # Remove postgresql:// prefix
            if db_url.startswith('postgresql://'):
                db_url = db_url[13:]
            
            # Split into parts
            if '@' in db_url:
                # Has authentication: postgresql://user:pass@host:port/db
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
                # No authentication: postgresql://host:port/db or postgresql://host/db
                username = password = ''
                if '/' in db_url:
                    host_port, database = db_url.rsplit('/', 1)
                    if ':' in host_port:
                        host, port = host_port.split(':', 1)
                    else:
                        host, port = host_port, '5432'
                else:
                    # Fallback: treat entire string as host
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
    
    def create_backup_directory(self):
        """Create backup directory if it doesn't exist."""
        try:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Backup directory: {self.backup_dir}")
        except Exception as e:
            logger.error(f"Failed to create backup directory: {e}")
            raise
    
    def generate_backup_filename(self, config: Dict[str, Any]) -> str:
        """Generate backup filename with timestamp."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        format_suffix = config.get('backup_format', 'custom')
        
        if format_suffix == 'custom':
            extension = '.backup'
        elif format_suffix == 'plain':
            extension = '.sql'
        elif format_suffix == 'directory':
            extension = '.dir'
        else:
            extension = '.backup'
        
        filename = f"expiry_tracker_backup_{timestamp}{extension}"
        
        if config.get('compression', True) and format_suffix != 'directory':
            filename += '.gz'
        
        return filename
    
    def run_pg_dump(self, db_config: Dict[str, str], backup_path: Path, config: Dict[str, Any]) -> bool:
        """Run pg_dump command to create backup."""
        try:
            # Build pg_dump command
            cmd = ['pg_dump']
            
            # Add connection parameters
            if db_config.get('host'):
                cmd.extend(['-h', db_config['host']])
            if db_config.get('port'):
                cmd.extend(['-p', db_config['port']])
            if db_config.get('username'):
                cmd.extend(['-U', db_config['username']])
            if db_config.get('database'):
                cmd.extend(['-d', db_config['database']])
            
            # Add format
            format_type = config.get('backup_format', 'custom')
            if format_type == 'custom':
                cmd.append('--format=custom')
            elif format_type == 'plain':
                cmd.append('--format=plain')
            elif format_type == 'directory':
                cmd.append('--format=directory')
            
            # Add options
            if config.get('include_schema', True) and not config.get('include_data', True):
                cmd.append('--schema-only')
            elif config.get('include_data', True) and not config.get('include_schema', True):
                cmd.append('--data-only')
            # If both are True (default), don't add either flag (backup everything)
            
            # Add custom options
            for option in config.get('pg_dump_options', []):
                cmd.append(option)
            
            # Add output file
            cmd.extend(['-f', str(backup_path)])
            
            # Set password environment variable
            env = os.environ.copy()
            if db_config.get('password'):
                env['PGPASSWORD'] = db_config['password']
            
            logger.info(f"Running pg_dump: {' '.join(cmd[:5])}...")
            
            # Run pg_dump
            result = subprocess.run(
                cmd,
                env=env,
                capture_output=True,
                text=True,
                timeout=3600  # 1 hour timeout
            )
            
            if result.returncode == 0:
                logger.info("Database backup completed successfully")
                return True
            else:
                logger.error(f"pg_dump failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("pg_dump timed out after 1 hour")
            return False
        except Exception as e:
            logger.error(f"Failed to run pg_dump: {e}")
            return False
    
    def compress_backup(self, backup_path: Path) -> bool:
        """Compress backup file if needed."""
        try:
            if backup_path.suffix == '.gz':
                return True  # Already compressed
            
            compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            with open(backup_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            backup_path.unlink()
            
            logger.info(f"Backup compressed: {compressed_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to compress backup: {e}")
            return False
    
    def create_backup(self, config: Dict[str, Any]) -> Optional[Path]:
        """Create a complete database backup."""
        try:
            # Get database URL
            db_url = self.get_database_url()
            if not db_url:
                logger.error("No database URL found")
                return None
            
            # Parse database URL
            db_config = self.parse_database_url(db_url)
            if not db_config:
                logger.error("Failed to parse database URL")
                return None
            
            # Create backup directory
            self.create_backup_directory()
            
            # Generate backup filename
            filename = self.generate_backup_filename(config)
            backup_path = self.backup_dir / filename
            
            # Create backup
            if not self.run_pg_dump(db_config, backup_path, config):
                return None
            
            # Compress if needed
            if config.get('compression', True) and not backup_path.suffix.endswith('.gz'):
                if not self.compress_backup(backup_path):
                    return None
                backup_path = backup_path.with_suffix(backup_path.suffix + '.gz')
            
            # Get file size
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info(f"Backup created: {backup_path} ({size_mb:.2f} MB)")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            return None
    
    def list_backups(self) -> List[Dict[str, Any]]:
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
    
    def cleanup_old_backups(self, config: Dict[str, Any]):
        """Remove old backups based on retention policy."""
        try:
            retention_days = config.get('backup_retention_days', 30)
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            backups = self.list_backups()
            removed_count = 0
            
            for backup in backups:
                if backup['created'] < cutoff_date:
                    try:
                        backup['path'].unlink()
                        logger.info(f"Removed old backup: {backup['filename']}")
                        removed_count += 1
                    except Exception as e:
                        logger.error(f"Failed to remove backup {backup['filename']}: {e}")
            
            if removed_count > 0:
                logger.info(f"Cleanup completed: removed {removed_count} old backups")
            else:
                logger.info("No old backups to remove")
                
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")

def main():
    """Main entry point for the backup script."""
    parser = argparse.ArgumentParser(
        description="Database backup and restore utility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/backup/backup_db.py              # Create backup
  python scripts/backup/backup_db.py --config-only # Show current config
  python scripts/backup/backup_db.py --list-backups # List available backups
  python scripts/backup/backup_db.py --cleanup    # Remove old backups
        """
    )
    
    parser.add_argument(
        '--config-only',
        action='store_true',
        help='Show current backup configuration'
    )
    
    parser.add_argument(
        '--list-backups',
        action='store_true',
        help='List all available backups'
    )
    
    parser.add_argument(
        '--cleanup',
        action='store_true',
        help='Remove old backups based on retention policy'
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
    
    # Initialize backup system
    backup_system = DatabaseBackup(app_root)
    config = backup_system.load_config()
    
    try:
        if args.config_only:
            print("Current backup configuration:")
            print(json.dumps(config, indent=2))
            return 0
        
        elif args.list_backups:
            backups = backup_system.list_backups()
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
        
        elif args.cleanup:
            backup_system.cleanup_old_backups(config)
            return 0
        
        else:
            # Create backup
            print("🚀 Creating database backup...")
            backup_path = backup_system.create_backup(config)
            
            if backup_path:
                print(f"✅ Backup created successfully: {backup_path}")
                
                # Cleanup old backups
                backup_system.cleanup_old_backups(config)
                
                return 0
            else:
                print("❌ Backup creation failed!")
                return 1
    
    except KeyboardInterrupt:
        print("\n⚠️ Backup operation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Backup operation failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 