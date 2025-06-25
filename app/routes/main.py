from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models.item import Item, STATUS_ACTIVE, STATUS_EXPIRED, STATUS_EXPIRING_SOON, STATUS_PENDING
from app.services.zoho_service import ZohoService
from app.services.activity_service import ActivityService
from datetime import datetime, timedelta
from app.models.user import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard route."""
    try:
        current_app.logger.info(f"User authenticated: {current_user.id}")
        
        # Get user's inventory items
        items = Item.query.filter_by(user_id=current_user.id).all()
        current_app.logger.info(f"Found {len(items)} items for user {current_user.id}")
        
        # Update item statuses with force_update to ensure consistency
        for item in items:
            current_app.logger.info(f"Updating status for item {item.id} ({item.name})")
            item.update_status(force_update=True)
            current_app.logger.info(f"Item {item.id} ({item.name}) current status: {item.status}")
        
        # Get expiring and expired items
        expiring_items = [item.to_dict() for item in items if item.status == STATUS_EXPIRING_SOON]
        expired_items = [item.to_dict() for item in items if item.status == STATUS_EXPIRED]
        active_items = [item.to_dict() for item in items if item.status == STATUS_ACTIVE]
        all_items_dict = [item.to_dict() for item in items]
        
        # Calculate total values for each category
        total_active_value = sum(item['quantity'] * item['cost_price'] for item in active_items if item['quantity'] and item['cost_price'])
        total_expiring_value = sum(item['quantity'] * item['cost_price'] for item in expiring_items if item['quantity'] and item['cost_price'])
        total_expired_value = sum(item['quantity'] * item['cost_price'] for item in expired_items if item['quantity'] and item['cost_price'])
        total_value = sum(item['quantity'] * item['cost_price'] for item in all_items_dict if item['quantity'] and item['cost_price'])
        
        current_app.logger.info(f"Expiring items: {len(expiring_items)}, Expired items: {len(expired_items)}, Active items: {len(active_items)}")
        
        # Get recent notifications using NotificationService
        from app.services.notification_service import NotificationService
        notification_service = NotificationService()
        notifications = notification_service.get_user_notifications(current_user.id, limit=5)
        
        # Get recent activities using ActivityService
        activity_service = ActivityService()
        activities = activity_service.get_recent_activities_for_dashboard(current_user.id, limit=5)
        
        return render_template('dashboard.html',
                            items=all_items_dict,
                            expiring_items=expiring_items,
                            expired_items=expired_items,
                            active_items=active_items,
                            total_active_value=total_active_value,
                            total_expiring_value=total_expiring_value,
                            total_expired_value=total_expired_value,
                            total_value=total_value,
                            notifications=notifications,
                            activities=activities)
        
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {str(e)}")
        flash('An error occurred while loading the dashboard.', 'error')
        return redirect(url_for('main.index'))

@main_bp.route('/inventory')
@login_required
def inventory():
    """Inventory management page."""
    try:
        # Try to sync with Zoho if connected
        if current_user.zoho_access_token:
            zoho_service = ZohoService(current_user)
            if current_user.zoho_token_expires_at and datetime.now() >= current_user.zoho_token_expires_at:
                if not zoho_service.refresh_token():
                    flash('Failed to refresh Zoho connection. Please reconnect in Settings.', 'error')
            else:
                # Get all items with Zoho IDs
                items_with_zoho = Item.query.filter(
                    Item.user_id == current_user.id,
                    Item.zoho_item_id.isnot(None)
                ).all()
                
                # Check status in Zoho for each item but don't delete immediately
                for item in items_with_zoho:
                    zoho_status = zoho_service.get_item_status(item.zoho_item_id)
                    if zoho_status == 'inactive' and item.status != STATUS_PENDING:
                        current_app.logger.info(f"Item {item.id} ({item.name}) is inactive in Zoho")
                        item.status = STATUS_PENDING
                        db.session.add(item)
                
                db.session.commit()
                
                # Now sync remaining items
                sync_success = zoho_service.sync_inventory(current_user)
                if not sync_success:
                    flash('Failed to sync with Zoho inventory. Please check your connection in Settings.', 'error')
        else:
            flash('Zoho sync is not available. Please connect in Settings to sync your inventory.', 'info')
        
        # Get user's items after potential updates
        # Build query
        query = Item.query.filter_by(user_id=current_user.id)
        
        # Get filter parameters
        status = request.args.get('status')
        search = request.args.get('search', '').strip()
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            query = query.filter(Item.name.ilike(search_term))
        
        # Apply sorting by expiry date
        query = query.order_by(Item.expiry_date.asc().nullslast())
        
        items = query.all()
        
        # Update item statuses with force_update to ensure consistency
        for item in items:
            current_app.logger.info(f"Updating status for item {item.id} ({item.name})")
            item.update_status(force_update=True)
            current_app.logger.info(f"Item {item.id} ({item.name}) current status: {item.status}")
        
        # Apply status filter after updating statuses
        if status:
            items = [item for item in items if item.status == status]
        
        return render_template('inventory.html',
                            items=items,
                            current_status=status,
                            current_search=search,
                            STATUS_ACTIVE=STATUS_ACTIVE,
                            STATUS_EXPIRED=STATUS_EXPIRED,
                            STATUS_EXPIRING_SOON=STATUS_EXPIRING_SOON,
                            STATUS_PENDING=STATUS_PENDING,
                            today_date=datetime.now().date().strftime('%Y-%m-%d'),
                            now=datetime.now(),
                            timedelta=timedelta)
        
    except Exception as e:
        current_app.logger.error(f"Inventory error: {str(e)}")
        flash('An error occurred while loading the inventory.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    """User settings page."""
    return render_template('settings.html')

@main_bp.route('/help')
def help():
    """Help and documentation page."""
    return render_template('help.html')

@main_bp.route('/contact')
def contact():
    """Contact page."""
    return render_template('contact.html')

@main_bp.route('/about')
def about():
    """About page."""
    return render_template('about.html') 