from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1.blueprint import api_bp
from app.core.extensions import db
from app.models.item import Item
from app.models.user import User
from app.services.zoho_service import ZohoService
from app.services.activity_service import ActivityService
from datetime import datetime
from typing import Dict, Any, Optional, List, cast
from flask_login import login_required, current_user
from flask import current_app
from sqlalchemy import and_, or_
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql import text

@api_bp.route('/items', methods=['POST'])
@login_required
def create_item():
    """Create a new item."""
    user_id = current_user.id
    user: Optional[User] = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    errors = validate_item_data(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    try:
        # Check if item already exists in local database
        existing_item = Item.query.filter_by(
            name=data['name'],
            user_id=user_id
        ).first()
        
        if existing_item:
            # Update existing item
            old_values = {
                'quantity': existing_item.quantity,
                'cost_price': existing_item.cost_price,
                'expiry_date': existing_item.expiry_date.isoformat() if existing_item.expiry_date else None
            }
            
            for key, value in data.items():
                if hasattr(existing_item, key):
                    setattr(existing_item, key, value)
            
            existing_item.update_status(force_update=True)
            db.session.commit()
            
            # Log activity for item update
            activity_service = ActivityService()
            changes = {k: v for k, v in data.items() if k in old_values and old_values[k] != v}
            if changes:
                activity_service.log_item_updated(user_id, existing_item.name, existing_item.id, changes)
            
            return jsonify({'message': 'Item updated successfully', 'item': existing_item.to_dict()})
        
        # Create new item
        item = Item(
            name=data['name'],
            description=data.get('description', ''),
            quantity=float(data.get('quantity', 0)),
            unit=data['unit'],
            selling_price=float(data['selling_price']),
            cost_price=float(data.get('cost_price', 0)),
            expiry_date=datetime.strptime(data['expiry_date'], '%Y-%m-%d').date(),
            status=data.get('status', 'active'),
            user_id=user_id
        )
        
        # Create item in Zoho
        zoho_service = ZohoService(user)
        zoho_item = zoho_service.create_item_in_zoho(data)
        
        if zoho_item:
            item.zoho_item_id = zoho_item['item_id']
        
        db.session.add(item)
        db.session.commit()
        
        # Log activity for item creation
        activity_service = ActivityService()
        activity_service.log_item_added(user_id, item.name, item.id)
        
        return jsonify({'message': 'Item created successfully', 'item': item.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/items/check', methods=['POST'])
@login_required
def check_item():
    """Check if an item with the given name exists."""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({'error': 'Name is required'}), 400
        
        name = data['name']
        current_app.logger.info(f"Checking for existing item with name: {name}")
        
        existing_item = Item.query.filter(
            Item.name.ilike(name),
            Item.user_id == current_user.id
        ).first()
        
        current_app.logger.info(f"Item exists: {existing_item is not None}")
        
        return jsonify({
            'exists': existing_item is not None,
            'item': existing_item.to_dict() if existing_item else None
        })
    except Exception as e:
        current_app.logger.error(f"Error checking item existence: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update an existing item."""
    user_id = current_user.id
    user: Optional[User] = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    item = Item.query.filter_by(id=item_id, user_id=user_id).first()
    if not item:
        return jsonify({'error': 'Item not found'}), 404
    
    data = request.get_json()
    errors = validate_item_data(data)
    if errors:
        return jsonify({'error': errors}), 400
    
    try:
        # Store old values for activity logging
        old_values = {
            'quantity': item.quantity,
            'cost_price': item.cost_price,
            'expiry_date': item.expiry_date.isoformat() if item.expiry_date else None,
            'selling_price': item.selling_price,
            'description': item.description
        }
        
        # Update item fields
        for key, value in data.items():
            if hasattr(item, key) and key != 'id' and key != 'user_id':
                if key == 'expiry_date' and value:
                    item.expiry_date = datetime.strptime(value, '%Y-%m-%d').date()
                elif key in ['quantity', 'cost_price', 'selling_price', 'discounted_price']:
                    setattr(item, key, float(value) if value is not None and value != '' else None)
                else:
                    setattr(item, key, value)
        
        # Update status
        item.update_status(force_update=True)
        
        # Update in Zoho if connected
        if user.zoho_access_token and item.zoho_item_id:
            zoho_service = ZohoService(user)
            zoho_service.update_item_in_zoho(item.zoho_item_id, data)
        
        db.session.commit()
        
        # Log activity for item update
        activity_service = ActivityService()
        changes = {k: v for k, v in data.items() if k in old_values and old_values[k] != v}
        if changes:
            activity_service.log_item_updated(user_id, item.name, item.id, changes)
        
        return jsonify({'message': 'Item updated successfully', 'item': item.to_dict()})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/items/<int:item_id>', methods=['GET'])
@login_required
def get_item(item_id):
    """Get a specific item by ID."""
    try:
        item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        return jsonify({'item': item.to_dict()})
    except Exception as e:
        current_app.logger.error(f"Error getting item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Delete an item."""
    try:
        item = Item.query.filter_by(id=item_id, user_id=current_user.id).first()
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        item_name = item.name
        item_id_for_log = item.id
        
        # Delete from Zoho if connected
        if current_user.zoho_access_token and item.zoho_item_id:
            zoho_service = ZohoService(cast(User, current_user))
            zoho_service.delete_item_in_zoho(item.zoho_item_id)
        
        db.session.delete(item)
        db.session.commit()
        
        # Log activity for item deletion
        activity_service = ActivityService()
        activity_service.log_item_deleted(current_user.id, item_name, item_id_for_log)
        
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting item: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/items/bulk-delete', methods=['POST'])
@login_required
def bulk_delete_items():
    """Delete multiple items at once."""
    try:
        data = request.get_json()
        if not data or 'item_ids' not in data:
            return jsonify({'error': 'No item IDs provided'}), 400
            
        raw_item_ids = data['item_ids']
        if not isinstance(raw_item_ids, list):
            return jsonify({'error': 'Item IDs must be a list of integers'}), 400
        item_ids = [i for i in raw_item_ids if isinstance(i, int)]
        if not item_ids:
            return jsonify({'error': 'No valid item IDs provided'}), 400
        id_filter = Item.id.in_(item_ids)
        id_filter = cast(BinaryExpression, id_filter)
        items = Item.query.filter(Item.user_id == current_user.id, id_filter).all()  # type: ignore
        
        if not items:
            return jsonify({'error': 'No valid items found'}), 404
            
        # If connected to Zoho, mark items as inactive
        if current_user.zoho_access_token:
            zoho_service = ZohoService(cast(User, current_user))
            for item in items:
                if item.zoho_item_id:
                    zoho_service.delete_item_in_zoho(item.zoho_item_id)
        
        # Delete items from database
        for item in items:
            db.session.delete(item)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Successfully deleted {len(items)} items'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in bulk delete: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/items/filter', methods=['GET'])
@login_required
def filter_items():
    """Filter and search items."""
    try:
        # Get filter parameters
        status: str = request.args.get('status', '')
        search: str = request.args.get('search', '').strip()
        price_range: str = request.args.get('price_range', '')
        quantity_status: str = request.args.get('quantity_status', '')
        date_range: str = request.args.get('date_range', '')
        sort_by: str = request.args.get('sort_by', 'expiry_date')  # Default sort by expiry date
        sort_order: str = request.args.get('sort_order', 'asc')  # Default ascending order
        
        current_app.logger.info(f"API: filter_items called - user_id: {current_user.id}, status: {status}, search: {search}, price_range: {price_range}, quantity_status: {quantity_status}, date_range: {date_range}, sort_by: {sort_by}, sort_order: {sort_order}")
        
        # Build query
        query = Item.query.filter_by(user_id=current_user.id)
        
        # Apply enhanced search filter (name and description)
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                db.or_(
                    Item.name.ilike(search_term),
                    Item.description.ilike(search_term)
                )
            )
        
        # Apply status filter
        if status and status.strip():
            query = query.filter(Item.status == status)
        
        # Apply price range filter
        if price_range and price_range.strip():
            if price_range == 'cost_under_50':
                query = query.filter(Item.cost_price < 50.0)
            elif price_range == 'cost_50_100':
                query = query.filter(Item.cost_price >= 50.0, Item.cost_price <= 100.0)
            elif price_range == 'cost_over_100':
                query = query.filter(Item.cost_price > 100.0)
            elif price_range == 'selling_under_50':
                query = query.filter(Item.selling_price < 50.0)
            elif price_range == 'selling_50_100':
                query = query.filter(Item.selling_price >= 50.0, Item.selling_price <= 100.0)
            elif price_range == 'selling_over_100':
                query = query.filter(Item.selling_price > 100.0)
        
        # Apply quantity status filter
        if quantity_status and quantity_status.strip():
            if quantity_status == 'low_stock':
                query = query.filter(Item.quantity < 10.0)
            elif quantity_status == 'out_of_stock':
                query = query.filter(Item.quantity == 0.0)
            elif quantity_status == 'well_stocked':
                query = query.filter(Item.quantity >= 10.0)
        
        # Apply date range filter
        if date_range and date_range.strip():
            from datetime import datetime, timedelta
            today = datetime.now().date()
            
            if date_range == '7_days':
                future_date = today + timedelta(days=7)
                query = query.filter(
                    Item.expiry_date.isnot(None),
                    Item.expiry_date <= future_date,
                    Item.expiry_date >= today
                )
            elif date_range == '30_days':
                future_date = today + timedelta(days=30)
                query = query.filter(
                    Item.expiry_date.isnot(None),
                    Item.expiry_date <= future_date,
                    Item.expiry_date >= today
                )
            elif date_range == '90_days':
                future_date = today + timedelta(days=90)
                query = query.filter(
                    Item.expiry_date.isnot(None),
                    Item.expiry_date <= future_date,
                    Item.expiry_date >= today
                )
            elif date_range == 'no_expiry':
                query = query.filter(Item.expiry_date.is_(None))
        
        # Apply sorting
        valid_sort_fields = {
            'name', 'quantity', 'cost_price', 'selling_price', 'status', 'expiry_date'
        }
        if sort_by not in valid_sort_fields:
            sort_by = 'expiry_date'
        sort_column = getattr(Item, sort_by, None)
        if sort_column is not None:
            if sort_order == 'desc':
                if sort_by == 'expiry_date':
                    query = query.order_by(sort_column.desc().nullslast())
                else:
                    query = query.order_by(sort_column.desc())
            else:
                if sort_by == 'expiry_date':
                    query = query.order_by(sort_column.asc().nullslast())
                else:
                    query = query.order_by(sort_column.asc())
        # else: do not apply ordering if column is not valid
        
        items = query.all()
        
        # Update item statuses to ensure consistency
        for item in items:
            item.update_status(force_update=True)
        
        current_app.logger.info(f"API: filter_items - found {len(items)} items")
        
        result = [item.to_dict() for item in items]
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"API: filter_items error - {str(e)}")
        return jsonify({'error': str(e)}), 500

def validate_item_data(data):
    errors = []
    name = data.get('name', '').strip()
    quantity = data.get('quantity')
    unit = data.get('unit', '').strip()
    cost_price = data.get('cost_price')
    selling_price = data.get('selling_price')
    discounted_price = data.get('discounted_price')
    expiry_date = data.get('expiry_date')
    description = data.get('description', '')

    if not name or len(name) > 100:
        errors.append('Name is required and must be less than 100 characters.')
    try:
        quantity_val = float(quantity)
        if quantity_val < 0:
            errors.append('Quantity must be a non-negative number.')
    except (TypeError, ValueError):
        errors.append('Quantity is required and must be a number.')
    if not unit or len(unit) > 20:
        errors.append('Unit is required and must be less than 20 characters.')
    try:
        cost_price_val = float(cost_price)
        if cost_price_val < 0:
            errors.append('Cost Price must be a non-negative number.')
    except (TypeError, ValueError):
        errors.append('Cost Price is required and must be a number.')
    try:
        selling_price_val = float(selling_price)
        if selling_price_val < 0:
            errors.append('Selling Price must be a non-negative number.')
    except (TypeError, ValueError):
        errors.append('Selling Price is required and must be a number.')
    
    # Validate discounted price if provided
    if discounted_price is not None and discounted_price != '':
        try:
            discounted_price_val = float(discounted_price)
            if discounted_price_val < 0:
                errors.append('Discounted Price must be a non-negative number.')
            elif discounted_price_val > selling_price_val:
                errors.append('Discounted Price cannot be higher than Selling Price.')
        except (TypeError, ValueError):
            errors.append('Discounted Price must be a valid number.')
    
    # Only validate expiry_date if it's provided (for updates, it's optional)
    if expiry_date:
        try:
            from datetime import datetime
            expiry = datetime.strptime(expiry_date, '%Y-%m-%d')
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            if expiry <= today:
                errors.append('Expiry date must be in the future.')
        except Exception:
            errors.append('Expiry date must be a valid date in YYYY-MM-DD format.')
    
    if description and len(description) > 500:
        errors.append('Description must be less than 500 characters.')
    return errors 