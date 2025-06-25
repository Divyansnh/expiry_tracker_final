#!/usr/bin/env python3
"""
Quick verification script for setup scripts

This script provides a simple way to verify that your setup scripts are ready
for use without running any actual setup operations.

Usage:
    python scripts/verify_setup.py
"""

import os
import sys
import subprocess
from pathlib import Path

def print_status(message, status="INFO"):
    """Print a status message with color."""
    colors = {
        "INFO": "\033[94m",    # Blue
        "SUCCESS": "\033[92m", # Green
        "WARNING": "\033[93m", # Yellow
        "ERROR": "\033[91m",   # Red
        "RESET": "\033[0m"     # Reset
    }
    print(f"{colors.get(status, '')}[{status}]{colors['RESET']} {message}")

def check_file_exists(file_path, description):
    """Check if a file exists and is readable."""
    path = Path(file_path)
    if path.exists() and path.is_file():
        print_status(f"✓ {description} exists", "SUCCESS")
        return True
    else:
        print_status(f"✗ {description} not found", "ERROR")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists."""
    path = Path(dir_path)
    if path.exists() and path.is_dir():
        print_status(f"✓ {description} exists", "SUCCESS")
        return True
    else:
        print_status(f"✗ {description} not found", "ERROR")
        return False

def check_script_permissions(script_path):
    """Check if a script has execute permissions."""
    path = Path(script_path)
    if path.exists():
        if os.access(path, os.X_OK):
            print_status(f"✓ {path.name} is executable", "SUCCESS")
            return True
        else:
            print_status(f"⚠ {path.name} exists but is not executable", "WARNING")
            return False
    else:
        print_status(f"✗ {path.name} not found", "ERROR")
        return False

def check_python_syntax(script_path):
    """Check Python script syntax."""
    try:
        result = subprocess.run([
            sys.executable, "-m", "py_compile", str(script_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status(f"✓ {script_path.name} syntax is valid", "SUCCESS")
            return True
        else:
            print_status(f"✗ {script_path.name} syntax error: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        print_status(f"✗ {script_path.name} syntax check failed: {e}", "ERROR")
        return False

def check_shell_syntax(script_path):
    """Check shell script syntax."""
    try:
        result = subprocess.run([
            "bash", "-n", str(script_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print_status(f"✓ {script_path.name} syntax is valid", "SUCCESS")
            return True
        else:
            print_status(f"✗ {script_path.name} syntax error: {result.stderr}", "ERROR")
            return False
    except Exception as e:
        print_status(f"✗ {script_path.name} syntax check failed: {e}", "ERROR")
        return False

def check_help_command(script_path, script_type):
    """Check if help command works."""
    try:
        if script_type == "python":
            cmd = [sys.executable, str(script_path), "--help"]
        else:
            cmd = [str(script_path), "--help"]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0 and "usage:" in result.stdout.lower():
            print_status(f"✓ {script_path.name} help command works", "SUCCESS")
            return True
        else:
            print_status(f"✗ {script_path.name} help command failed", "ERROR")
            return False
    except Exception as e:
        print_status(f"✗ {script_path.name} help command failed: {e}", "ERROR")
        return False

def main():
    """Main verification function."""
    print_status("🔍 Verifying Setup Scripts", "INFO")
    print_status("This script checks if your setup scripts are ready for use.", "INFO")
    print_status("", "INFO")
    
    # Track results
    checks_passed = 0
    total_checks = 0
    
    # Check 1: Required files exist
    print_status("=== Checking Required Files ===", "INFO")
    
    files_to_check = [
        ("requirements.txt", "Requirements file"),
        ("run.py", "Application entry point"),
        ("app/__init__.py", "Flask application factory"),
        ("app/config.py", "Configuration file"),
        ("migrations/env.py", "Database migrations"),
    ]
    
    for file_path, description in files_to_check:
        total_checks += 1
        if check_file_exists(file_path, description):
            checks_passed += 1
    
    print_status("", "INFO")
    
    # Check 2: Required directories exist
    print_status("=== Checking Required Directories ===", "INFO")
    
    dirs_to_check = [
        ("app", "Application directory"),
        ("migrations", "Migrations directory"),
        ("scripts", "Scripts directory"),
    ]
    
    for dir_path, description in dirs_to_check:
        total_checks += 1
        if check_directory_exists(dir_path, description):
            checks_passed += 1
    
    print_status("", "INFO")
    
    # Check 3: Setup scripts exist and are valid
    print_status("=== Checking Setup Scripts ===", "INFO")
    
    # Python setup script
    python_script = Path("scripts/setup.py")
    total_checks += 1
    if check_file_exists(python_script, "Python setup script"):
        checks_passed += 1
        total_checks += 1
        if check_python_syntax(python_script):
            checks_passed += 1
        total_checks += 1
        if check_help_command(python_script, "python"):
            checks_passed += 1
    
    # Shell setup script
    shell_script = Path("scripts/setup.sh")
    total_checks += 1
    if check_file_exists(shell_script, "Shell setup script"):
        checks_passed += 1
        total_checks += 1
        if check_shell_syntax(shell_script):
            checks_passed += 1
        total_checks += 1
        if check_script_permissions(shell_script):
            checks_passed += 1
        total_checks += 1
        if check_help_command(shell_script, "shell"):
            checks_passed += 1
    
    print_status("", "INFO")
    
    # Check 4: Test script exists
    print_status("=== Checking Test Scripts ===", "INFO")
    
    test_script = Path("scripts/quick_test.py")
    total_checks += 1
    if check_file_exists(test_script, "Quick test script"):
        checks_passed += 1
        total_checks += 1
        if check_python_syntax(test_script):
            checks_passed += 1
    
    print_status("", "INFO")
    
    # Check 5: Documentation exists
    print_status("=== Checking Documentation ===", "INFO")
    
    docs_to_check = [
        ("scripts/README.md", "Scripts documentation"),
        ("README.md", "Main README"),
    ]
    
    for doc_path, description in docs_to_check:
        total_checks += 1
        if check_file_exists(doc_path, description):
            checks_passed += 1
    
    print_status("", "INFO")
    
    # Print summary
    print_status("=" * 50, "INFO")
    print_status("VERIFICATION SUMMARY", "INFO")
    print_status("=" * 50, "INFO")
    
    success_rate = (checks_passed / total_checks) * 100 if total_checks > 0 else 0
    
    if checks_passed == total_checks:
        print_status("🎉 ALL CHECKS PASSED!", "SUCCESS")
        print_status(f"Passed: {checks_passed}/{total_checks} ({success_rate:.1f}%)", "SUCCESS")
        print_status("Your setup scripts are ready for use!", "SUCCESS")
        print_status("", "INFO")
        print_status("Next steps:", "INFO")
        print_status("1. Test the scripts: python scripts/quick_test.py", "INFO")
        print_status("2. Share your repository with others", "INFO")
        print_status("3. Users can run: python scripts/setup.py", "INFO")
        return 0
    else:
        print_status("❌ SOME CHECKS FAILED", "ERROR")
        print_status(f"Passed: {checks_passed}/{total_checks} ({success_rate:.1f}%)", "ERROR")
        print_status("Please fix the issues above before sharing your repository.", "ERROR")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 