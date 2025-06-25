#!/usr/bin/env python3
"""
Demo Data Setup Script for Expiry Tracker Portfolio
This script creates comprehensive demo data showcasing all features.
"""

import sys
import os
from datetime import datetime, timedelta, date
import random

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.models.user import User
from app.models.item import Item
from app.models.notification import Notification
from app.models.report import Report
from app.models.activity import Activity
from app.core.extensions import db

def setup_full_demo_data():
    """Create comprehensive demo data showcasing all features."""
    print("🚀 Setting up full demo data for Expiry Tracker...")
    
    # Create a demo-specific app configuration
    app = create_app('development')
    
    # Override the database URI to use a separate demo database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///demo.db'
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {}  # Remove PostgreSQL-specific options
    
    with app.app_context():
        try:
            # Check if demo data already exists
            try:
                demo_admin = User.query.filter_by(username='demo_admin').first()
                if demo_admin:
                    print("⚠️  Demo data already exists. Skipping setup.")
                    return
            except Exception:
                # If query fails, continue with setup
                pass
            
            print("📝 Creating demo users...")
            # Create demo users
            demo_users = [
                User(username='demo_admin', email='admin@demo-expiry-tracker.com', is_verified=True),
                User(username='demo_user', email='user@demo-expiry-tracker.com', is_verified=True),
                User(username='demo_manager', email='manager@demo-expiry-tracker.com', is_verified=True)
            ]
            
            for user in demo_users:
                user.password = 'Demo123!'
                db.session.add(user)
            
            db.session.commit()
            print(f"✅ Created {len(demo_users)} demo users")
            
            # Create demo items for each user
            print("📦 Creating demo inventory items...")
            categories = ['Dairy', 'Meat', 'Fruits', 'Vegetables', 'Bakery', 'Beverages', 'Snacks', 'Frozen Foods', 'Pantry', 'Condiments']
            
            items_data = [
                # Fresh items (7-14 days)
                {'name': 'Organic Whole Milk', 'category': 'Dairy', 'days': 7, 'quantity': 2, 'unit': 'liters'},
                {'name': 'Free Range Chicken Breast', 'category': 'Meat', 'days': 3, 'quantity': 500, 'unit': 'grams'},
                {'name': 'Fresh Red Apples', 'category': 'Fruits', 'days': 14, 'quantity': 6, 'unit': 'pieces'},
                {'name': 'Organic Spinach', 'category': 'Vegetables', 'days': 5, 'quantity': 200, 'unit': 'grams'},
                {'name': 'Whole Grain Sourdough Bread', 'category': 'Bakery', 'days': 4, 'quantity': 1, 'unit': 'loaf'},
                {'name': 'Fresh Orange Juice', 'category': 'Beverages', 'days': 10, 'quantity': 1, 'unit': 'liter'},
                {'name': 'Greek Yogurt Natural', 'category': 'Dairy', 'days': 8, 'quantity': 4, 'unit': 'pots'},
                {'name': 'Fresh Strawberries', 'category': 'Fruits', 'days': 6, 'quantity': 250, 'unit': 'grams'},
                {'name': 'Baby Carrots', 'category': 'Vegetables', 'days': 9, 'quantity': 300, 'unit': 'grams'},
                {'name': 'Artisan Croissants', 'category': 'Bakery', 'days': 2, 'quantity': 4, 'unit': 'pieces'},
                
                # Expiring soon (1-2 days)
                {'name': 'Lean Ground Beef', 'category': 'Meat', 'days': 1, 'quantity': 300, 'unit': 'grams'},
                {'name': 'Ripe Bananas', 'category': 'Fruits', 'days': 2, 'quantity': 8, 'unit': 'pieces'},
                {'name': 'Mixed Salad Greens', 'category': 'Vegetables', 'days': 1, 'quantity': 1, 'unit': 'bag'},
                {'name': 'Fresh Pasta', 'category': 'Pantry', 'days': 2, 'quantity': 500, 'unit': 'grams'},
                
                # Expired items (for demonstration)
                {'name': 'Expired Milk', 'category': 'Dairy', 'days': -2, 'quantity': 1, 'unit': 'liter'},
                {'name': 'Old White Bread', 'category': 'Bakery', 'days': -3, 'quantity': 1, 'unit': 'loaf'},
                {'name': 'Spoiled Chicken Thighs', 'category': 'Meat', 'days': -1, 'quantity': 400, 'unit': 'grams'},
                {'name': 'Moldy Cheese', 'category': 'Dairy', 'days': -5, 'quantity': 200, 'unit': 'grams'},
                
                # Long shelf life items
                {'name': 'Extra Virgin Olive Oil', 'category': 'Condiments', 'days': 365, 'quantity': 1, 'unit': 'bottle'},
                {'name': 'Organic Honey', 'category': 'Pantry', 'days': 730, 'quantity': 500, 'unit': 'grams'},
                {'name': 'Dark Chocolate Bars', 'category': 'Snacks', 'days': 180, 'quantity': 5, 'unit': 'bars'},
                {'name': 'Frozen Mixed Vegetables', 'category': 'Frozen Foods', 'days': 90, 'quantity': 1, 'unit': 'kg'},
                {'name': 'Canned Tomatoes', 'category': 'Pantry', 'days': 547, 'quantity': 6, 'unit': 'cans'},
            ]
            
            for user in demo_users:
                for item_data in items_data:
                    item = Item(
                        name=item_data['name'],
                        expiry_date=datetime.now() + timedelta(days=item_data['days']),
                        quantity=item_data['quantity'],
                        category=item_data['category'],
                        unit=item_data['unit'],
                        user_id=user.id,
                        created_at=datetime.now() - timedelta(days=random.randint(1, 30))
                    )
                    db.session.add(item)
            
            db.session.commit()
            print(f"✅ Created {len(items_data) * len(demo_users)} inventory items")
            
            # Create demo notifications
            print("🔔 Creating demo notifications...")
            for user in demo_users:
                notification_data = [
                    {
                        'message': "Ground Beef expires in 1 day. Consider using it today!",
                        'type': "in_app",
                        'priority': "high",
                        'status': "pending"
                    },
                    {
                        'message': "You have 3 items expiring this week. Check your inventory!",
                        'type': "in_app",
                        'priority': "normal",
                        'status': "sent"
                    },
                    {
                        'message': "Organic Milk has been added to your inventory.",
                        'type': "in_app",
                        'priority': "normal",
                        'status': "pending"
                    },
                    {
                        'message': "Expired Milk has been detected in your inventory.",
                        'type': "in_app",
                        'priority': "high",
                        'status': "pending"
                    }
                ]
                for data in notification_data:
                    notification = Notification()
                    notification.message = data['message']
                    notification.type = data['type']
                    notification.priority = data['priority']
                    notification.user_id = user.id
                    notification.status = data['status']
                    notification.created_at = datetime.now() - timedelta(hours=random.randint(1, 48))
                    db.session.add(notification)
            
            db.session.commit()
            print(f"✅ Created {len(notification_data) * len(demo_users)} notifications")
            
            # Create demo reports
            print("📊 Creating demo reports...")
            for user in demo_users:
                reports = [
                    Report(
                        user_id=user.id,
                        date=date.today() - timedelta(days=7),
                        total_items=25,
                        total_value=150.0,
                        expiring_items=3,
                        expired_items=1,
                        low_stock_items=2,
                        total_sales=200.0,
                        total_purchases=100.0,
                        report_data={"summary": "Weekly report"},
                        is_public=False
                    ),
                    Report(
                        user_id=user.id,
                        date=date.today() - timedelta(days=1),
                        total_items=22,
                        total_value=120.0,
                        expiring_items=2,
                        expired_items=2,
                        low_stock_items=1,
                        total_sales=180.0,
                        total_purchases=90.0,
                        report_data={"summary": "Expired items report"},
                        is_public=False
                    ),
                    Report(
                        user_id=user.id,
                        date=date.today() - timedelta(days=30),
                        total_items=30,
                        total_value=200.0,
                        expiring_items=5,
                        expired_items=0,
                        low_stock_items=3,
                        total_sales=300.0,
                        total_purchases=150.0,
                        report_data={"summary": "Monthly analytics report"},
                        is_public=True
                    )
                ]
                for report in reports:
                    db.session.add(report)
            
            db.session.commit()
            print(f"✅ Created {len(reports) * len(demo_users)} reports")
            
            # Create demo activities
            print("📝 Creating demo activity logs...")
            for user in demo_users:
                activities_data = [
                    {
                        'activity_type': Activity.LOGIN,
                        'title': "User logged in successfully",
                        'description': "User logged in successfully"
                    },
                    {
                        'activity_type': Activity.ITEM_ADDED,
                        'title': "Added Organic Milk to inventory",
                        'description': "Added Organic Milk to inventory"
                    },
                    {
                        'activity_type': Activity.ITEM_UPDATED,
                        'title': "Updated quantity for Fresh Apples",
                        'description': "Updated quantity for Fresh Apples"
                    },
                    {
                        'activity_type': Activity.REPORT_GENERATED,
                        'title': "Generated weekly inventory report",
                        'description': "Generated weekly inventory report"
                    },
                    {
                        'activity_type': Activity.NOTIFICATION_SENT,
                        'title': "Sent expiry warning notification",
                        'description': "Sent expiry warning notification"
                    }
                ]
                for data in activities_data:
                    activity = Activity()
                    activity.user_id = user.id
                    activity.activity_type = data['activity_type']
                    activity.title = data['title']
                    activity.description = data['description']
                    activity.created_at = datetime.now() - timedelta(hours=random.randint(1, 24))
                    db.session.add(activity)
            
            db.session.commit()
            print(f"✅ Created {len(activities_data) * len(demo_users)} activity logs")
            
            print("\n🎉 Demo data setup completed successfully!")
            print("\n📋 Demo Credentials:")
            print("=" * 50)
            for user in demo_users:
                print(f"👤 {user.username}: {user.email}")
                print(f"   Password: Demo123!")
            print("=" * 50)
            
            print("\n🔍 Features to Showcase:")
            print("✅ User Authentication & Registration")
            print("✅ Email Verification System")
            print("✅ Inventory Management (Add/Edit/Delete)")
            print("✅ Category-based Organization")
            print("✅ Expiry Date Tracking")
            print("✅ Quantity & Unit Management")
            print("✅ Search & Filter Functionality")
            print("✅ Email Notifications")
            print("✅ Report Generation")
            print("✅ Activity Logging")
            print("✅ Responsive Design")
            print("✅ RESTful API Endpoints")
            
            print("\n📊 Demo Data Summary:")
            print(f"• {len(demo_users)} users with different roles")
            print(f"• {len(items_data) * len(demo_users)} inventory items")
            print(f"• Items across {len(categories)} categories")
            print(f"• Items with various expiry dates (fresh, expiring, expired)")
            print(f"• {len(notification_data) * len(demo_users)} notifications")
            print(f"• {len(reports) * len(demo_users)} reports")
            print(f"• {len(activities_data) * len(demo_users)} activity logs")
            
        except Exception as e:
            print(f"❌ Error setting up demo data: {str(e)}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    setup_full_demo_data() 