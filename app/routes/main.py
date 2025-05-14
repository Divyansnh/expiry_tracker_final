from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify, current_app
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models.item import Item, STATUS_ACTIVE, STATUS_EXPIRED, STATUS_EXPIRING_SOON, STATUS_PENDING
from app.models.notification import Notification
from app.services.notification_service import NotificationService
from app.services.zoho_service import ZohoService
from datetime import datetime, timedelta
from flask import session
from app.models.user import User
import secrets

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
        notification_service = NotificationService()
        notifications = notification_service.get_user_notifications(current_user.id, limit=5)
        
        return render_template('dashboard.html',
                            items=all_items_dict,
                            expiring_items=expiring_items,
                            expired_items=expired_items,
                            active_items=active_items,
                            total_active_value=total_active_value,
                            total_expiring_value=total_expiring_value,
                            total_expired_value=total_expired_value,
                            total_value=total_value,
                            notifications=notifications)
        
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
        
        # Apply status filter
        if status:
            if status == 'expiring_soon':
                query = query.filter(Item.status == STATUS_EXPIRING_SOON)
            elif status == 'expired':
                query = query.filter(Item.status == STATUS_EXPIRED)
            elif status == 'active':
                query = query.filter(Item.status == STATUS_ACTIVE)
            elif status == 'pending':
                query = query.filter(Item.status == STATUS_PENDING)
        
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
        
        return render_template('inventory.html',
                            items=items,
                            current_status=status,
                            current_search=search,
                            STATUS_ACTIVE=STATUS_ACTIVE,
                            STATUS_EXPIRED=STATUS_EXPIRED,
                            STATUS_EXPIRING_SOON=STATUS_EXPIRING_SOON,
                            STATUS_PENDING=STATUS_PENDING,
                            today_date=datetime.now().date().strftime('%Y-%m-%d'))
        
    except Exception as e:
        current_app.logger.error(f"Inventory error: {str(e)}")
        flash('An error occurred while loading the inventory.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/notifications')
@login_required
def notifications():
    """Notifications page."""
    notification_service = NotificationService()
    notifications = notification_service.get_user_notifications(current_user.id)
    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification_service = NotificationService()
    success = notification_service.mark_notification_read(notification_id, current_user.id)
    
    if success:
        flash('Notification marked as read', 'success')
    else:
        flash('Notification not found', 'error')
    
    return redirect(url_for('main.notifications'))

@main_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """User settings page."""
    if request.method == 'POST':
        try:
            # Update username
            new_username = request.form.get('username')
            if new_username and new_username != current_user.username:
                if User.query.filter_by(username=new_username).first():
                    flash('Username already exists', 'error')
                    return redirect(url_for('main.settings'))
                current_user.username = new_username
            
            # Update email
            new_email = request.form.get('email')
            if new_email and new_email != current_user.email:
                if User.query.filter_by(email=new_email).first():
                    flash('Email already exists', 'error')
                    return redirect(url_for('main.settings'))
                current_user.email = new_email
            
            # Update password if provided
            new_password = request.form.get('new_password')
            if new_password:
                confirm_password = request.form.get('confirm_password')
                if new_password != confirm_password:
                    flash('Passwords do not match', 'error')
                    return redirect(url_for('main.settings'))
                try:
                    current_user.password = new_password  # This will validate password strength
                except ValueError as e:
                    flash(str(e), 'error')
                    return redirect(url_for('main.settings'))
            
            # Update Zoho credentials if provided
            new_zoho_client_id = request.form.get('zoho_client_id')
            new_zoho_client_secret = request.form.get('zoho_client_secret')
            
            if new_zoho_client_id or new_zoho_client_secret:
                # Check for duplicate credentials
                existing_user = User.query.filter(
                    User.zoho_client_id == new_zoho_client_id,
                    User.zoho_client_secret == new_zoho_client_secret,
                    User.id != current_user.id
                ).first()
                
                if existing_user:
                    flash('These Zoho credentials are already in use by another user. Please use different credentials.', 'error')
                    return redirect(url_for('main.settings'))
                
                # If no duplicates found, update the credentials
                if new_zoho_client_id:
                    current_user.zoho_client_id = new_zoho_client_id
                if new_zoho_client_secret:
                    current_user.zoho_client_secret = new_zoho_client_secret
            
            db.session.commit()
            flash('Account settings updated successfully!', 'success')
            return redirect(url_for('main.settings'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error updating settings: {str(e)}")
            flash('An error occurred while updating settings', 'error')
            return redirect(url_for('main.settings'))
    
    return render_template('settings.html')

@main_bp.route('/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    """Update notification preferences."""
    try:
        current_user.email_notifications = request.form.get('email_notifications') == 'on'
        current_user.save()
        
        flash('Notification settings updated successfully', 'success')
    except Exception as e:
        flash(f'Error updating notification settings: {str(e)}', 'error')
    
    return redirect(url_for('main.settings'))

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

def format_to_title_case(name: str) -> str:
    """Format a string to Title Case."""
    if not name:
        return ""
    return ' '.join(word.capitalize() for word in name.lower().split())

@main_bp.route('/add_item', methods=['POST'])
@login_required
def add_item():
    """Add a new item to the inventory."""
    try:
        # Handle both form data and JSON requests
        if request.is_json:
            data = request.get_json()
        else:
            data = {
                'name': request.form.get('name', ''),
                'quantity': request.form.get('quantity'),
                'unit': request.form.get('unit'),
                'selling_price': request.form.get('selling_price'),
                'cost_price': request.form.get('cost_price'),
                'description': request.form.get('description'),
                'expiry_date': request.form.get('expiry_date')
            }
        
        # Format the name to Title Case
        if data['name']:
            data['name'] = format_to_title_case(data['name'])
        
        current_app.logger.info(f"Received add_item request with data: {data}")
        
        # Validate required fields
        required_fields = ['name', 'quantity', 'unit', 'selling_price', 'expiry_date']
        for field in required_fields:
            if field not in data or not data[field]:
                current_app.logger.error(f"Missing required field: {field}")
                if request.is_json:
                    return jsonify({'error': f'Missing required field: {field}'}), 400
                else:
                    flash(f'Missing required field: {field}', 'error')
                    return redirect(url_for('main.add_item'))
        
        # Validate expiry date format
        try:
            expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        except ValueError:
            current_app.logger.error("Invalid expiry date format")
            if request.is_json:
                return jsonify({'error': 'Invalid expiry date format. Use YYYY-MM-DD'}), 400
            else:
                flash('Invalid expiry date format. Use YYYY-MM-DD', 'error')
                return redirect(url_for('main.add_item'))
        
        # Check if item already exists in database
        existing_item = Item.query.filter_by(name=data['name'], user_id=current_user.id).first()
        
        if existing_item:
            current_app.logger.info(f"Item '{data['name']}' already exists. Updating...")
            
            # Update item in Zoho first
            zoho_service = ZohoService(current_user)
            zoho_response = zoho_service.update_item_in_zoho(existing_item.zoho_item_id, data)
            
            if not zoho_response:
                current_app.logger.error("Failed to update item in Zoho")
                if request.is_json:
                    return jsonify({'error': 'Failed to update item in Zoho'}), 500
                else:
                    flash('Failed to update item in Zoho', 'error')
                    return redirect(url_for('main.inventory'))
            
            # Update local database
            existing_item.quantity = float(data['quantity'])
            existing_item.unit = data['unit']
            existing_item.selling_price = float(data['selling_price'])
            existing_item.cost_price = float(data.get('cost_price', 0))
            existing_item.description = data.get('description', '')
            existing_item.expiry_date = expiry_date
            
            # Update status based on expiry date
            current_date = datetime.now().date()
            if expiry_date <= current_date:
                existing_item.status = STATUS_EXPIRED
            else:
                existing_item.status = STATUS_ACTIVE
            
            db.session.commit()
            current_app.logger.info(f"Successfully updated item: {existing_item.name}")
            
            if request.is_json:
                return jsonify({'message': 'Item updated successfully', 'item': existing_item.to_dict()})
            else:
                flash('Item updated successfully', 'success')
                return redirect(url_for('main.inventory'))
        
        # Create new item in Zoho first
        zoho_service = ZohoService(current_user)
        zoho_item = zoho_service.create_item_in_zoho(data)
        
        if not zoho_item:
            current_app.logger.error("Failed to create item in Zoho")
            if request.is_json:
                return jsonify({'error': 'Failed to create item in Zoho'}), 500
            else:
                flash('Failed to create item in Zoho', 'error')
                return redirect(url_for('main.inventory'))
        
        # Create new item in local database
        new_item = Item(
            name=data['name'],
            quantity=float(data['quantity']),
            unit=data['unit'],
            selling_price=float(data['selling_price']),
            cost_price=float(data.get('cost_price', 0)),
            description=data.get('description', ''),
            expiry_date=expiry_date,
            zoho_item_id=zoho_item['item_id'],
            status=STATUS_ACTIVE if expiry_date > datetime.now().date() else STATUS_EXPIRED,
            user_id=current_user.id
        )
        
        db.session.add(new_item)
        db.session.commit()
        
        current_app.logger.info(f"Successfully created new item: {new_item.name}")
        
        if request.is_json:
            return jsonify({'message': 'Item added successfully', 'item': new_item.to_dict()})
        else:
            flash('Item added successfully', 'success')
            return redirect(url_for('main.inventory'))
        
    except Exception as e:
        current_app.logger.error(f"Error in add_item: {str(e)}")
        if request.is_json:
            return jsonify({'error': str(e)}), 500
        else:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('main.inventory'))

@main_bp.route('/update_item/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update an existing item."""
    try:
        item = Item.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # Format the name to Title Case if it's being updated
        if 'name' in data:
            data['name'] = format_to_title_case(data['name'])
        
        # Update item in local database
        item.name = data.get('name', item.name)
        
        # Handle numeric fields with None checks
        if 'quantity' in data:
            item.quantity = float(data['quantity']) if data['quantity'] is not None else 0.0
        if 'selling_price' in data:
            item.selling_price = float(data['selling_price']) if data['selling_price'] is not None else None
        if 'cost_price' in data:
            item.cost_price = float(data['cost_price']) if data['cost_price'] is not None else None
        if 'discounted_price' in data:
            # Handle empty string, None, or zero
            if data['discounted_price'] is None or data['discounted_price'] == '' or data['discounted_price'] == '0':
                item.discounted_price = None
            else:
                # Convert to float and round to 2 decimal places
                try:
                    price = float(data['discounted_price'])
                    # Only set if price is greater than 0
                    item.discounted_price = round(price, 2) if price > 0 else None
                except (ValueError, TypeError):
                    item.discounted_price = None
            
        item.unit = data.get('unit', item.unit)
        item.description = data.get('description', item.description)
        if 'expiry_date' in data:
            # Convert string to date object
            item.expiry_date = datetime.strptime(data['expiry_date'], '%Y-%m-%d').date()
        
        # Update status based on expiry date
        item.update_status(force_update=True)
        
        db.session.commit()
        
        # Only sync with Zoho if this is not an edit operation (i.e., not from the edit button)
        if current_user.zoho_access_token and item.zoho_item_id and not request.headers.get('X-Edit-Operation'):
            zoho_service = ZohoService(current_user)
            # Prepare data for Zoho update
            zoho_data = {
                'name': item.name,
                'unit': item.unit,
                'quantity': item.quantity,
                'description': item.description,
                'selling_price': item.selling_price,
                'cost_price': item.cost_price,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                'status': 'inactive' if item.status == STATUS_EXPIRED else 'active'
            }
            
            if zoho_service.update_item_in_zoho(item.zoho_item_id, zoho_data):
                current_app.logger.info(f"Successfully synced item {item.id} with Zoho")
                flash('Item updated successfully and synced with Zoho', 'success')
            else:
                current_app.logger.warning(f"Failed to sync item {item.id} with Zoho")
                flash('Item updated locally but failed to sync with Zoho', 'warning')
        else:
            current_app.logger.info(f"Successfully updated item {item.id} locally")
            flash('Item updated successfully', 'success')
        
        return jsonify({'success': True, 'item': item.to_dict()})
        
    except ValueError as e:
        db.session.rollback()
        current_app.logger.error(f"Invalid data format: {str(e)}")
        return jsonify({'success': False, 'error': 'Invalid data format'}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating item: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/delete_item/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete an item."""
    try:
        item = Item.query.get_or_404(item_id)
        
        # Check if user owns the item
        if item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # If connected to Zoho and item has a Zoho ID, mark it as inactive in Zoho
        if current_user.zoho_access_token and item.zoho_item_id:
            zoho_service = ZohoService(current_user)
            if not zoho_service.delete_item_in_zoho(item.zoho_item_id):
                current_app.logger.error(f"Failed to mark item {item.id} as inactive in Zoho")
                return jsonify({'success': False, 'error': 'Failed to delete item in Zoho'}), 500
        
        # Delete from local database
        db.session.delete(item)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Item deleted successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error deleting item: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Failed to delete item'}), 500

@main_bp.route('/get_item/<int:item_id>')
@login_required
def get_item(item_id):
    """Get item details for editing."""
    try:
        item = Item.query.get_or_404(item_id)
        if item.user_id != current_user.id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
            
        # Get Zoho status if connected
        zoho_status = None
        if current_user.zoho_access_token and item.zoho_item_id:
            try:
                zoho_service = ZohoService(current_user)
                zoho_status = zoho_service.get_item_status(item.zoho_item_id)
            except Exception as e:
                current_app.logger.warning(f"Could not get Zoho status for item {item_id}: {str(e)}")
                zoho_status = None
            
        # Format the expiry date properly
        formatted_expiry_date = None
        if item.expiry_date:
            if isinstance(item.expiry_date, datetime):
                formatted_expiry_date = item.expiry_date.date().strftime('%Y-%m-%d')
            else:
                formatted_expiry_date = item.expiry_date.strftime('%Y-%m-%d')
            
        return jsonify({
            'success': True,
            'item': {
                'id': item.id,
                'name': item.name,
                'quantity': float(item.quantity) if item.quantity is not None else 0,
                'unit': item.unit,
                'selling_price': float(item.selling_price) if item.selling_price is not None else 0,
                'cost_price': float(item.cost_price) if item.cost_price is not None else 0,
                'discounted_price': float(item.discounted_price) if item.discounted_price is not None else None,
                'description': item.description or '',
                'expiry_date': formatted_expiry_date,
                'status': item.status,
                'zoho_status': zoho_status
            }
        })
    except Exception as e:
        current_app.logger.error(f"Error getting item details: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to load item details'}), 500

@main_bp.route('/settings/zoho-credentials', methods=['POST'])
@login_required
def update_zoho_credentials():
    """Update user's Zoho client credentials."""
    try:
        new_zoho_client_id = request.form.get('zoho_client_id')
        new_zoho_client_secret = request.form.get('zoho_client_secret')
        
        # Check for duplicate credentials
        existing_user = User.query.filter(
            User.zoho_client_id == new_zoho_client_id,
            User.zoho_client_secret == new_zoho_client_secret,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            flash('These Zoho credentials are already in use by another user. Please use different credentials.', 'error')
            return redirect(url_for('main.settings'))
        
        # If no duplicates found, update the credentials
        current_user.zoho_client_id = new_zoho_client_id
        current_user.zoho_client_secret = new_zoho_client_secret
        db.session.commit()
        
        flash('Zoho credentials updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating Zoho credentials: {str(e)}")
        flash('An error occurred while updating Zoho credentials', 'error')
    
    return redirect(url_for('main.settings'))

@main_bp.route('/api/v1/items/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_items():
    """Delete multiple items at once."""
    try:
        # Check if user is authenticated via session
        if not current_user.is_authenticated:
            return jsonify({'error': 'Authentication required'}), 401
            
        data = request.get_json()
        if not data or 'item_ids' not in data:
            return jsonify({'error': 'No item IDs provided'}), 400
            
        item_ids = data['item_ids']
        if not isinstance(item_ids, list):
            return jsonify({'error': 'Item IDs must be a list'}), 400
            
        if len(item_ids) > 20:
            return jsonify({'error': 'Cannot delete more than 20 items at once'}), 400
            
        # Get all items that belong to the current user
        items = Item.query.filter(
            Item.id.in_(item_ids),
            Item.user_id == current_user.id
        ).all()
        
        if not items:
            return jsonify({'error': 'No valid items found'}), 404
            
        # If connected to Zoho, mark items as inactive
        if current_user.zoho_access_token:
            zoho_service = ZohoService(current_user)
            for item in items:
                if item.zoho_item_id:
                    zoho_service.delete_item_in_zoho(item.zoho_item_id)
        
        # Delete items from database
        for item in items:
            db.session.delete(item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Successfully deleted {len(items)} items'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk delete: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@main_bp.route('/sync-inventory', methods=['GET', 'POST'])
@login_required
def sync_inventory():
    """Sync inventory with Zoho."""
    user = current_user
    if not user.zoho_credentials:
        flash('Please configure Zoho credentials first.', 'error')
        return redirect(url_for('main.zoho_settings'))
    
    try:
        zoho_service = ZohoService(user.zoho_credentials)
        result = zoho_service.sync_inventory()
        flash(f'Successfully synced {result["synced"]} items with Zoho.', 'success')
    except Exception as e:
        flash(f'Error syncing with Zoho: {str(e)}', 'error')
    
    return redirect(url_for('main.index')) 