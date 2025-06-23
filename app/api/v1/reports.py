from flask import jsonify, request
from flask_login import login_required, current_user
from app.api.v1.blueprint import api_bp
from app.core.extensions import db
from app.services.report_service import ReportService
from app.models.report import Report
from datetime import datetime, timedelta
from flask import current_app

report_service = ReportService()

@api_bp.route('/reports', methods=['GET'])
@login_required
def get_reports():
    """Get user's reports."""
    try:
        # Get pagination parameters
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=20, type=int)
        
        # Check if date filter is explicitly provided
        has_start_date = request.args.get('start_date') is not None
        has_end_date = request.args.get('end_date') is not None
        
        # Only apply date filter if dates are explicitly provided
        if has_start_date or has_end_date:
            # Get date range from query parameters
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=30)  # Default fallback
            
            if has_start_date:
                start_date_str = request.args.get('start_date')
                if start_date_str:
                    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            if has_end_date:
                end_date_str = request.args.get('end_date')
                if end_date_str:
                    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            
            current_app.logger.info(f"API: get_reports called with date filter - user_id: {current_user.id}, page: {page}, per_page: {per_page}, start_date: {start_date}, end_date: {end_date}")
            
            # Get reports with date filter and pagination
            reports, total_count = report_service.get_reports_by_date_range_paginated(start_date, end_date, current_user.id, page, per_page)
        else:
            # No date filter - get all reports
            current_app.logger.info(f"API: get_reports called without date filter - user_id: {current_user.id}, page: {page}, per_page: {per_page}")
            
            # Get all reports with pagination
            reports, total_count = report_service.get_all_reports_paginated(current_user.id, page, per_page)
        
        current_app.logger.info(f"API: get_reports - found {len(reports)} reports, total: {total_count}")
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page  # Ceiling division
        
        result = [report.to_dict() for report in reports]
        
        return jsonify({
            'reports': result,
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
        current_app.logger.error(f"API: get_reports error - {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate a new report for the current user."""
    try:
        current_app.logger.info(f"API: generate_report called - user_id: {current_user.id}")
        
        report = report_service.generate_daily_report(current_user.id)
        if report:
            current_app.logger.info(f"API: generate_report - successfully generated report {report.id}")
            return jsonify({
                'message': 'Report generated successfully',
                'report': report.to_dict()
            })
        
        current_app.logger.error(f"API: generate_report - failed to generate report")
        return jsonify({'error': 'Failed to generate report'}), 500
        
    except Exception as e:
        current_app.logger.error(f"API: generate_report error - {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/<int:report_id>', methods=['GET'])
@login_required
def get_report(report_id):
    """Get a specific report."""
    try:
        current_app.logger.info(f"API: get_report called - user_id: {current_user.id}, report_id: {report_id}")
        
        report = report_service.get_report(report_id)
        if not report or report.user_id != current_user.id:
            return jsonify({'error': 'Report not found'}), 404
        
        current_app.logger.info(f"API: get_report - found report {report_id}")
        
        return jsonify({'report': report.to_dict()})
        
    except Exception as e:
        current_app.logger.error(f"API: get_report error - {str(e)}")
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reports/<int:report_id>', methods=['DELETE'])
@login_required
def delete_report(report_id):
    """Delete a specific report."""
    try:
        current_app.logger.info(f"API: delete_report called - user_id: {current_user.id}, report_id: {report_id}")
        
        report = report_service.get_report(report_id)
        if not report or report.user_id != current_user.id:
            return jsonify({'error': 'Report not found'}), 404
            
        db.session.delete(report)
        db.session.commit()
        
        current_app.logger.info(f"API: delete_report - successfully deleted report {report_id}")
        return jsonify({'message': 'Report deleted successfully'})
        
    except Exception as e:
        current_app.logger.error(f"API: delete_report error - {str(e)}")
        db.session.rollback()
        return jsonify({'error': str(e)}), 500 