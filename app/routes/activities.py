from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from app.services.activity_service import ActivityService
from app.core.extensions import db

activities_bp = Blueprint('activities', __name__)

@activities_bp.route('/activities')
@login_required
def activities():
    """Activity log page showing user's recent activities."""
    return render_template('activities.html')

@activities_bp.route('/api/v1/activities')
@login_required
def get_activities():
    """Get paginated activities for the current user."""
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        activity_type = request.args.get('type', 'all')
        
        activity_service = ActivityService()
        activities, total_count = activity_service.get_activities_paginated(
            current_user.id, 
            page=page, 
            per_page=per_page,
            activity_type=activity_type
        )
        
        return jsonify({
            'activities': activities,
            'total': total_count,
            'page': page,
            'per_page': per_page,
            'pages': (total_count + per_page - 1) // per_page
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500 