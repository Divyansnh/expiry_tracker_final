from datetime import datetime
from flask import current_app
from app.services.report_service import ReportService
from app.models.user import User

def generate_daily_report():
    """Generate daily inventory report at midnight."""
    try:
        current_app.logger.info("Starting daily report generation")
        report_service = ReportService()
        
        # Get all users
        users = User.query.all()
        current_app.logger.info(f"Found {len(users)} users for report generation")
        
        # Generate report for each user
        for user in users:
            report = report_service.generate_daily_report(user.id)
            if report:
                current_app.logger.info(f"Successfully generated report for user {user.id} on {report.date}")
            else:
                current_app.logger.error(f"Failed to generate daily report for user {user.id}")
            
    except Exception as e:
        current_app.logger.error(f"Error in daily report generation: {str(e)}") 