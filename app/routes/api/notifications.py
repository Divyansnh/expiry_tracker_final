from flask import Blueprint, jsonify
from flask_login import login_required, current_user
from app.models.notification import Notification

bp = Blueprint('notifications', __name__)

@bp.route('/notifications', methods=['GET'])
@login_required
def get_notifications():
    """Get all notifications for the current user."""
    notifications = Notification.query.filter_by(
        user_id=current_user.id
    ).order_by(Notification.created_at.desc()).all()
    
    return jsonify({
        'notifications': [n.to_dict() for n in notifications]
    })

@bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """Mark a notification as read."""
    notification = Notification.query.filter_by(
        id=notification_id,
        user_id=current_user.id
    ).first_or_404()
    
    notification.mark_as_read()
    return jsonify({'success': True})

@bp.route('/notifications/read-all', methods=['POST'])
@login_required
def mark_all_notifications_read():
    """Mark all notifications as read."""
    notifications = Notification.query.filter_by(
        user_id=current_user.id,
        status='pending'
    ).all()
    
    for notification in notifications:
        notification.mark_as_read()
    
    return jsonify({'success': True}) 