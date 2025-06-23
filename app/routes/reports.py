from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify, request, current_app, url_for
from flask_login import login_required, current_user
from app.services.report_service import ReportService
from app.core.extensions import db

reports_bp = Blueprint('reports', __name__)
report_service = ReportService()

@reports_bp.route('/reports')
@login_required
def reports():
    """View all reports."""
    # Get date range from query parameters or default to last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    reports = report_service.get_reports_by_date_range(start_date, end_date, current_user.id)
    return render_template('reports.html', reports=reports)

@reports_bp.route('/reports/<int:report_id>')
@login_required
def view_report(report_id):
    """View a specific report."""
    report = report_service.get_report(report_id)
    if not report or report.user_id != current_user.id:
        return jsonify({'error': 'Report not found'}), 404
    return render_template('view_report.html', report=report, is_public=report.is_public) 