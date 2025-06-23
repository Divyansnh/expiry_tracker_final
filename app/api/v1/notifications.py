from flask import jsonify, request
from flask_login import login_required, current_user
from app.api.v1.blueprint import api_bp
from app.core.extensions import db
from app.models.notification import Notification
from app.models.user import User
from app.services.notification_service import NotificationService
from flask_wtf.csrf import generate_csrf
from datetime import datetime, timedelta
from app.models.item import Item
from typing import cast
from flask import current_app

@api_bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get user's notifications."""
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)  # Increased from 10 to 20
        show_sent = request.args.get('show_sent', 'false').lower() == 'true'
        filter_type = request.args.get('filter', 'all')  # all, sent, pending
        search = request.args.get('search', '').strip()  # Search term
        search_mode = request.args.get('search_mode', 'message')  # Search mode
        
        current_app.logger.info(f"API: get_notifications called - user_id: {current_user.id}, page: {page}, per_page: {per_page}, show_sent: {show_sent}, filter: {filter_type}, search: '{search}', search_mode: {search_mode}")
        
        notification_service = NotificationService()
        
        # Get notifications based on filter type with pagination and search
        if filter_type == 'sent':
            notifications, total_count = notification_service.get_user_notifications_paginated(current_user.id, page, per_page, show_sent=True, search=search if search else None, search_mode=search_mode)
        elif filter_type == 'pending':
            notifications, total_count = notification_service.get_user_notifications_paginated(current_user.id, page, per_page, show_sent=False, search=search if search else None, search_mode=search_mode)
        else:  # 'all'
            notifications, total_count = notification_service.get_user_notifications_all_paginated(current_user.id, page, per_page, search=search if search else None, search_mode=search_mode)
        
        # Get total counts for stats
        total_sent = notification_service.get_notification_count(current_user.id, 'sent')
        total_pending = notification_service.get_notification_count(current_user.id, 'pending')
        total_all = total_sent + total_pending
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        
        current_app.logger.info(f"API: get_notifications - found {len(notifications)} notifications, total: {total_count}, pages: {total_pages}")
        
        result = [notification.to_dict() for notification in notifications]
        current_app.logger.info(f"API: get_notifications - returning {len(result)} notifications")
        
        return jsonify({
            'notifications': result,
            'stats': {
                'total_sent': total_sent,
                'total_pending': total_pending,
                'total_all': total_all
            },
            'pagination': {
                'current_page': page,
                'per_page': per_page,
                'total_count': total_count,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })
    except Exception as e:
        current_app.logger.error(f"API: get_notifications error - {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/notifications/<int:notification_id>/read', methods=['PUT'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    try:
        notification = Notification.query.filter_by(
            id=notification_id,
            user_id=current_user.id
        ).first()
        
        if not notification:
            return jsonify({'error': 'Notification not found'}), 404
            
        # Use the mark_as_read method
        notification.mark_as_read()
        return jsonify({'message': 'Notification marked as read'})
    except Exception as e:
        current_app.logger.error(f"Error marking notification as read: {str(e)}")
        return jsonify({'error': 'Failed to mark notification as read'}), 500

@api_bp.route('/notifications/read-all', methods=['PUT'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    try:
        # Update all pending notifications to sent status
        Notification.query.filter_by(
            user_id=current_user.id,
            status='pending'
        ).update({'status': 'sent'})
        db.session.commit()
        return jsonify({'message': 'All notifications marked as read'})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error marking notifications as read: {str(e)}")
        return jsonify({'error': 'Failed to mark notifications as read'}), 500

@api_bp.route('/notifications/preferences', methods=['GET'])
@login_required
def get_notification_preferences():
    """Get user's notification preferences."""
    return jsonify({
        'email_notifications': current_user.email_notifications
    })

@api_bp.route('/notifications/preferences', methods=['PUT'])
@login_required
def update_notification_preferences():
    """Update user's notification preferences."""
    if not request.is_json:
        return jsonify({'error': 'Missing JSON in request'}), 400
        
    data = request.get_json()
    
    try:
        if 'email_notifications' in data:
            current_user.email_notifications = data['email_notifications']
        
        current_user.save()
        return jsonify({'message': 'Notification preferences updated'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@api_bp.route('/notifications/test', methods=['POST'])
@login_required
def test_notifications():
    """Test notification delivery."""
    if not request.is_json:
        return jsonify({'error': 'Missing JSON in request'}), 400
        
    data = request.get_json()
    notification_type = data.get('type', 'email')  # Default to email if not specified
    
    if notification_type != 'email':
        return jsonify({'error': 'Invalid notification type'}), 400
        
    notification_service = NotificationService()
    
    try:
        # Create a test item for the notification
        test_item = Item(
            name='Test Item',
            expiry_date=datetime.utcnow() + timedelta(days=1),
            user_id=current_user.id
        )
        db.session.add(test_item)
        db.session.commit()
        
        # Create notification using the service
        notification = notification_service.create_notification(
            user_id=current_user.id,
            item_id=test_item.id,
            message='This is a test notification',
            type=notification_type,
            priority='normal'
        )
        
        if notification:
            # Send notification based on type
            if notification_type == 'email':
                # Cast current_user to User type since we know it's a User when @login_required
                user = cast(User, current_user)
                success = notification_service.send_daily_notification_email(
                    user,
                    [{
                        'id': test_item.id,
                        'name': test_item.name,
                        'days_until_expiry': 1,
                        'expiry_date': test_item.expiry_date
                    }]
                )
            
            if success:
                return jsonify({'message': 'Test notification sent successfully'})
            return jsonify({'error': 'Failed to send test notification'}), 500
        return jsonify({'error': 'Failed to create test notification'}), 500
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 