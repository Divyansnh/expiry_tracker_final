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

@reports_bp.route('/reports/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate a new report for the current user."""
    try:
        current_app.logger.info(f"Generating new report for user {current_user.id}")
        report = report_service.generate_daily_report(current_user.id)
        if report:
            current_app.logger.info(f"Successfully generated report {report.id} for user {current_user.id}")
            return jsonify({
                'message': 'Report generated successfully',
                'report_id': report.id,
                'redirect_url': url_for('reports.view_report', report_id=report.id)
            })
        current_app.logger.error(f"Failed to generate report for user {current_user.id}")
        return jsonify({'error': 'Failed to generate report - no report was created'}), 500
    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Error generating report: {error_msg}")
        return jsonify({
            'error': 'Failed to generate report',
            'details': error_msg
        }), 500

@reports_bp.route('/reports/<int:report_id>')
@login_required
def view_report(report_id):
    """View a specific report."""
    report = report_service.get_report(report_id)
    if not report or report.user_id != current_user.id:
        return jsonify({'error': 'Report not found'}), 404
    return render_template('view_report.html', report=report, is_public=report.is_public)

@reports_bp.route('/reports/<int:report_id>/delete', methods=['POST'])
@login_required
def delete_report(report_id):
    """Delete a specific report."""
    try:
        report = report_service.get_report(report_id)
        if not report or report.user_id != current_user.id:
            return jsonify({'error': 'Report not found'}), 404
            
        db.session.delete(report)
        db.session.commit()
        current_app.logger.info(f"Successfully deleted report {report_id}")
        return jsonify({'message': 'Report deleted successfully'})
    except Exception as e:
        current_app.logger.error(f"Error deleting report: {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 