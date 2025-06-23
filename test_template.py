#!/usr/bin/env python3

from app import create_app
from app.models.report import Report
from flask import render_template

def test_template_rendering():
    app = create_app()
    
    with app.app_context():
        # Get the first report
        report = Report.query.first()
        if not report:
            print("No reports found in database")
            return
        
        print(f"Testing template rendering for report {report.id}")
        print(f"Report data keys: {list(report.report_data.keys()) if report.report_data else 'No data'}")
        
        if report.report_data and 'expiry_analysis' in report.report_data:
            expiry_data = report.report_data['expiry_analysis']
            print(f"Expiry analysis keys: {list(expiry_data.keys())}")
            
            if 'categories' in expiry_data:
                print("✓ New report structure detected")
            elif 'next_week' in expiry_data or 'next_month' in expiry_data or 'next_quarter' in expiry_data:
                print("✓ Old report structure detected")
            else:
                print("? Unknown expiry analysis structure")
        
        # Create a test request context
        with app.test_request_context('/'):
            try:
                # Try to render the template
                html = render_template('view_report.html', report=report, is_public=report.is_public)
                print("✓ Template rendered successfully!")
                return True
            except Exception as e:
                print(f"✗ Template rendering failed: {e}")
                import traceback
                traceback.print_exc()
                return False

if __name__ == "__main__":
    test_template_rendering() 