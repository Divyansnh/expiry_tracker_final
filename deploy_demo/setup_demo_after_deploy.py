#!/usr/bin/env python3
"""
Simple demo setup script to run after deployment.
This script can be run via Render's shell or manually.
"""

import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def setup_demo():
    """Set up demo data after deployment."""
    try:
        from deploy_demo.setup_full_demo import setup_full_demo_data
        print("🚀 Setting up demo data...")
        setup_full_demo_data()
        print("✅ Demo setup completed!")
    except Exception as e:
        print(f"❌ Error setting up demo: {str(e)}")
        print("You can manually run: python deploy_demo/setup_full_demo.py")

if __name__ == "__main__":
    setup_demo() 