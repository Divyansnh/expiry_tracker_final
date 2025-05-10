import os
import shutil
from datetime import datetime
import subprocess
from pathlib import Path
import getpass

def create_backup():
    """Create a backup of the PostgreSQL database."""
    try:
        # Get the root directory (2 levels up from this script)
        root_dir = Path(__file__).resolve().parent.parent.parent
        
        # Create backup directory if it doesn't exist
        backup_dir = root_dir / 'scripts' / 'db' / 'backups'
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'expiry_tracker_v2_backup_{timestamp}.sql'
        backup_path = backup_dir / backup_filename
        
        # Create backup using pg_dump
        print(f"Creating backup of PostgreSQL database...")
        print(f"Destination: {backup_path}")
        
        # Get current username
        username = getpass.getuser()
        
        # Run pg_dump command
        cmd = [
            'pg_dump',
            '-h', 'localhost',
            '-U', username,  # Use current system username
            '-d', 'expiry_tracker_v2',
            '-f', str(backup_path)
        ]
        
        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"Backup created successfully: {backup_filename}")
            
            # Get backup size
            backup_size = backup_path.stat().st_size
            print(f"Backup size: {backup_size / 1024:.2f} KB")
            
            # List all backups
            print("\nAvailable backups:")
            for backup in sorted(backup_dir.glob('*.sql')):
                backup_time = datetime.fromtimestamp(backup.stat().st_mtime)
                backup_size = backup.stat().st_size
                print(f"- {backup.name} ({backup_size / 1024:.2f} KB) - Created: {backup_time}")
            
            return True
        else:
            print(f"Error creating backup: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error creating backup: {str(e)}")
        return False

if __name__ == "__main__":
    create_backup() 