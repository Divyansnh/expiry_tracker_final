from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.services.notification_service import NotificationService

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications')
@login_required
def notifications():
    """Notifications page."""
    # Get query parameters for initial state
    show_sent = request.args.get('show_sent', 'false').lower() == 'true'
    
    # Return the template - data will be loaded via API
    return render_template('notifications.html', show_sent=show_sent) 