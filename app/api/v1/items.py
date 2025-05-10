from flask import jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.api.v1 import api_bp
from app.core.extensions import db
from app.models.item import Item
from app.models.user import User
from app.services.zoho_service import ZohoService
from datetime import datetime
from typing import Dict, Any, Optional
from flask_login import login_required, current_user
from flask import current_app

@api_bp.route('/items', methods=['POST'])
@jwt_required()
def create_item():
    """Create a new item."""
    user_id = get_jwt_identity()
    user: Optional[User] = User.query.get(user_id)
    
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    data = request.get_json()
    
    try:
        # Check if item already exists in local database
        existing_item = Item.query.filter_by(
            name=data['name'],
            user_id=user_id
        ).first()
        
        if existing_item:
            # Update existing item
            for key, value in data.items():
                if hasattr(existing_item, key):
                    setattr(existing_item, key, value)
            
            existing_item.update_status(force_update=True)
            db.session.commit()
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