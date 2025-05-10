from datetime import datetime, timedelta, date
import secrets
from typing import Dict, List, Optional
from flask import current_app
from app.core.extensions import db
from app.models.report import Report
from app.models.item import Item
from app.models.user import User

class ReportService:
    """Service for generating and managing inventory reports."""
    
    def generate_daily_report(self, user_id: int) -> Optional[Report]:
        """Generate a daily inventory report for a specific user."""
        try:
            current_date = datetime.now().date()
            
            # Delete any existing report for today and user
            existing_report = Report.query.filter_by(date=current_date, user_id=user_id).first()
            if existing_report:
                try:
                    current_app.logger.info(f"Deleting existing report for user {user_id} on {current_date}")
                    db.session.delete(existing_report)
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Failed to delete existing report: {str(e)}")
                    db.session.rollback()
                    raise Exception(f"Could not delete existing report: {str(e)}")
            
            # Get all items for the user
            items = Item.query.filter_by(user_id=user_id).all()
            current_app.logger.info(f"Found {len(items)} items for user {user_id}")
            
            # Calculate report metrics
            total_items = len(items)
            expiring_items = len([item for item in items if item.is_near_expiry])
            expired_items = len([item for item in items if item.is_expired])
            low_stock_items = len([item for item in items if (item.quantity or 0) < 10])
            
            current_app.logger.info(f"Calculated metrics - Total: {total_items}, Expiring: {expiring_items}, Expired: {expired_items}, Low Stock: {low_stock_items}")
            
            # Calculate expiry risk metrics
            critical_items = [item for item in items if item.is_near_expiry and (item.quantity or 0) > 10]
            high_value_expiring = [item for item in items if item.is_near_expiry and (item.quantity or 0) * (item.cost_price or 0) > 1000]
            
            current_app.logger.info(f"Risk metrics - Critical: {len(critical_items)}, High Value: {len(high_value_expiring)}")
            
            # Group items by expiry timeframes
            expiry_timeframes = {
                'next_week': [],
                'next_month': [],
                'next_quarter': []
            }
            
            for item in items:
                if not item.expiry_date:
                    continue
                days = item.days_until_expiry
                if days is None:
                    continue
                    
                if 0 < days <= 7:
                    expiry_timeframes['next_week'].append(item)
                elif 7 < days <= 30:
                    expiry_timeframes['next_month'].append(item)
                elif 30 < days <= 90:
                    expiry_timeframes['next_quarter'].append(item)
            
            current_app.logger.info(f"Expiry timeframes - Week: {len(expiry_timeframes['next_week'])}, Month: {len(expiry_timeframes['next_month'])}, Quarter: {len(expiry_timeframes['next_quarter'])}")
            
            # Calculate historical comparison (last 7 days)
            last_week = datetime.now().date() - timedelta(days=7)
            last_week_report = Report.query.filter_by(user_id=user_id, date=last_week).first()
            
            # Prepare detailed report data
            report_data = {
                'summary': {
                    'total_items': total_items,
                    'expiring_items': expiring_items,
                    'expired_items': expired_items,
                    'low_stock_items': low_stock_items,
                    'critical_items': len(critical_items),
                    'high_value_expiring': len(high_value_expiring)
                },
                'expiry_analysis': {
                    'next_week': {
                        'count': len(expiry_timeframes['next_week']),
                        'items': [
                            {
                                'id': item.id,
                                'name': item.name,
                                'quantity': item.quantity,
                                'unit': item.unit,
                                'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
                                'days_until_expiry': item.days_until_expiry,
                                'location': item.location,
                                'batch_number': item.batch_number,
                                'value': (item.quantity or 0) * (item.cost_price or 0)
                            }
                            for item in expiry_timeframes['next_week']
                        ]
                    },
                    'next_month': {
                        'count': len(expiry_timeframes['next_month']),
                        'items': [
                            {
                                'id': item.id,
                                'name': item.name,
                                'quantity': item.quantity,
                                'unit': item.unit,
                                'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
                                'days_until_expiry': item.days_until_expiry,
                                'location': item.location,
                                'batch_number': item.batch_number,
                                'value': (item.quantity or 0) * (item.cost_price or 0)
                            }
                            for item in expiry_timeframes['next_month']
                        ]
                    },
                    'next_quarter': {
                        'count': len(expiry_timeframes['next_quarter']),
                        'items': [
                            {
                                'id': item.id,
                                'name': item.name,
                                'quantity': item.quantity,
                                'unit': item.unit,
                                'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
                                'days_until_expiry': item.days_until_expiry,
                                'location': item.location,
                                'batch_number': item.batch_number,
                                'value': (item.quantity or 0) * (item.cost_price or 0)
                            }
                            for item in expiry_timeframes['next_quarter']
                        ]
                    }
                },
                'risk_analysis': {
                    'critical_items': [
                        {
                            'id': item.id,
                            'name': item.name,
                            'quantity': item.quantity,
                            'unit': item.unit,
                            'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
                            'days_until_expiry': item.days_until_expiry,
                            'location': item.location,
                            'batch_number': item.batch_number,
                            'value': (item.quantity or 0) * (item.cost_price or 0)
                        }
                        for item in critical_items
                    ],
                    'high_value_expiring': [
                        {
                            'id': item.id,
                            'name': item.name,
                            'quantity': item.quantity,
                            'unit': item.unit,
                            'expiry_date': item.expiry_date.strftime('%Y-%m-%d'),
                            'days_until_expiry': item.days_until_expiry,
                            'location': item.location,
                            'batch_number': item.batch_number,
                            'value': (item.quantity or 0) * (item.cost_price or 0)
                        }
                        for item in high_value_expiring
                    ]
                },
                'historical_comparison': {
                    'last_week': {
                        'expiring_items': last_week_report.expiring_items if last_week_report else 0,
                        'expired_items': last_week_report.expired_items if last_week_report else 0,
                        'low_stock_items': last_week_report.low_stock_items if last_week_report else 0
                    } if last_week_report else None
                },
                'action_recommendations': [
                    {
                        'type': 'urgent',
                        'message': f'Take immediate action on {len(expiry_timeframes["next_week"])} items expiring in the next week',
                        'item_ids': [item.id for item in expiry_timeframes['next_week']]
                    },
                    {
                        'type': 'high_priority',
                        'message': f'Review {len(critical_items)} critical items with high quantity and near expiry',
                        'item_ids': [item.id for item in critical_items]
                    },
                    {
                        'type': 'value_protection',
                        'message': f'Consider discounting {len(high_value_expiring)} high-value items approaching expiry',
                        'item_ids': [item.id for item in high_value_expiring]
                    }
                ]
            }
            
            current_app.logger.info(f"Generated report data with {len(report_data['action_recommendations'])} recommendations")
            
            # Create report
            try:
                report = Report(
                    date=current_date,
                    user_id=user_id,
                    total_items=total_items,
                    total_value=0.0,
                    expiring_items=expiring_items,
                    expired_items=expired_items,
                    low_stock_items=low_stock_items,
                    total_sales=0.0,
                    total_purchases=0.0,
                    report_data=report_data,
                    is_public=False,
                    public_token=secrets.token_urlsafe(32)
                )
                
                db.session.add(report)
                db.session.commit()
                
                current_app.logger.info(f"Successfully generated and saved report for user {user_id} on {current_date}")
                return report
            except Exception as e:
                current_app.logger.error(f"Error saving report: {str(e)}")
                db.session.rollback()
                raise Exception(f"Failed to save report: {str(e)}")
            
        except Exception as e:
            current_app.logger.error(f"Error generating daily report: {str(e)}")
            db.session.rollback()
            raise
    
    def get_report(self, report_id: int) -> Optional[Report]:
        """Get report by ID."""
        report = Report.query.get(report_id)
        if report:
            if report.report_data is None:
                current_app.logger.warning(f"Report {report_id} has no report_data, initializing empty dict")
                report.report_data = {}
            else:
                current_app.logger.info(f"Retrieved report {report_id} with data: {report.report_data}")
        else:
            current_app.logger.warning(f"Report {report_id} not found")
        return report
    
    def get_latest_report(self, user_id: int) -> Optional[Report]:
        """Get the most recent report for a user."""
        return Report.query.filter_by(user_id=user_id).order_by(Report.date.desc()).first()
    
    def get_reports_by_date_range(self, start_date: date, end_date: date, user_id: int) -> List[Report]:
        """Get reports within a date range for a specific user."""
        return Report.query.filter(
            Report.date >= start_date,
            Report.date <= end_date,
            Report.user_id == user_id
        ).order_by(Report.date.desc()).all()
    
    def make_report_public(self, report_id: int) -> bool:
        """Make a report publicly accessible."""
        try:
            report = Report.query.get_or_404(report_id)
            report.is_public = True
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error making report public: {str(e)}")
            db.session.rollback()
            return False
    
    def get_public_report(self, token: str) -> Optional[Report]:
        """Get a report by its public token."""
        return Report.query.filter_by(public_token=token, is_public=True).first() 