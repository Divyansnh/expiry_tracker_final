from datetime import datetime, timedelta, date
import secrets
from typing import Dict, List, Optional, Any
from flask import current_app
from app.core.extensions import db
from app.models.report import Report
from app.models.item import Item, STATUS_ACTIVE, STATUS_EXPIRING_SOON, STATUS_EXPIRED
from app.models.user import User

class ReportService:
    """Service for generating and managing inventory reports."""
    
    def _calculate_risk_score(self, item) -> float:
        """Calculate risk score for an item (0-100) based on industry standards.
        
        Risk factors:
        - Expiry risk (40%): Based on days until expiry
        - Quantity risk (30%): Based on MOQ, safety stock, and current levels
        - Value risk (30%): Based on item value and carrying costs
        """
        if not item.days_until_expiry or item.days_until_expiry <= 0:
            return 100  # Expired items get maximum risk score
            
        score = 0
        quantity = item.quantity or 0
        value = quantity * (item.cost_price or 0)
        
        # 1. Expiry Risk (40% weight)
        if 0 < item.days_until_expiry <= 7:
            score += 40  # Critical: Within 7 days
        elif 8 <= item.days_until_expiry <= 14:
            score += 30  # High: Within 2 weeks
        elif 15 <= item.days_until_expiry <= 30:
            score += 20  # Medium: Within 1 month
        elif 31 <= item.days_until_expiry <= 60:
            score += 10  # Low: Within 2 months
            
        # 2. Quantity Risk (30% weight)
        # Use default values if attributes don't exist
        min_order_qty = getattr(item, 'min_order_quantity', 10)
        safety_stock = getattr(item, 'safety_stock', 5)
        
        if quantity <= safety_stock:
            score += 30  # Critical: Below safety stock
        elif quantity <= min_order_qty:
            score += 20  # High: Below MOQ
        elif quantity <= min_order_qty * 2:
            score += 10  # Medium: Below 2x MOQ
            
        # 3. Value Risk (30% weight)
        # Simple value-based risk assessment
        if value > 10000:  # High value items
            score += 30
        elif value > 5000:  # Medium value items
            score += 20
        elif value > 1000:  # Low value items
            score += 10
            
        # Additional risk factors (use getattr to safely check attributes)
        if getattr(item, 'is_critical', False):  # Critical items get +10 points
            score += 10
        if getattr(item, 'requires_refrigeration', False):  # Temperature-sensitive items get +10 points
            score += 10
            
        return min(score, 100)  # Cap at 100
    
    def _calculate_value_at_risk(self, items: List[Item]) -> Dict[str, Any]:
        """Calculate Value-at-Risk (VaR) analysis for inventory.
        
        This analysis focuses on:
        1. High-value items at risk of expiry
        2. Items with high quantity and near expiry
        3. Total value at risk in different timeframes
        
        Timeframes:
        - Immediate (7 days)
        - Short-term (30 days)
        - Medium-term (90 days)
        """
        try:
            # Initialize risk categories
            immediate_risk = []  # Items expiring in 7 days
            short_term_risk = []  # Items expiring in 30 days
            medium_term_risk = []  # Items expiring in 90 days
            high_quantity_risk = []  # Items with high quantity and near expiry
            
            for item in items:
                value = (item.quantity or 0) * (item.cost_price or 0)
                days_until_expiry = item.days_until_expiry or float('inf')
                quantity = item.quantity or 0
                
                # Skip items with no expiry date
                if days_until_expiry == float('inf'):
                    continue
                
                item_data = {
                    'id': item.id,
                    'name': item.name,
                    'quantity': quantity,
                    'unit': item.unit,
                    'value': value,
                    'days_until_expiry': days_until_expiry,
                    'cost_price': item.cost_price,
                    'location': item.location,
                    'batch_number': item.batch_number
                }
                
                # Categorize by risk timeframe
                if 0 < days_until_expiry <= 7:
                    immediate_risk.append(item_data)
                elif 7 < days_until_expiry <= 30:
                    short_term_risk.append(item_data)
                elif 30 < days_until_expiry <= 90:
                    medium_term_risk.append(item_data)
            
                # Identify high quantity items at risk
                if quantity > 100 and days_until_expiry <= 30:
                    high_quantity_risk.append(item_data)
            
            # Calculate total values
            total_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items)
            immediate_value = sum(item['value'] for item in immediate_risk)
            short_term_value = sum(item['value'] for item in short_term_risk)
            medium_term_value = sum(item['value'] for item in medium_term_risk)
            high_quantity_value = sum(item['value'] for item in high_quantity_risk)
            
            # Calculate percentages
            immediate_percentage = (immediate_value / total_value * 100) if total_value > 0 else 0
            short_term_percentage = (short_term_value / total_value * 100) if total_value > 0 else 0
            medium_term_percentage = (medium_term_value / total_value * 100) if total_value > 0 else 0
            high_quantity_percentage = (high_quantity_value / total_value * 100) if total_value > 0 else 0
            
            result = {
                'immediate_risk': {
                    'items': immediate_risk,
                    'value': immediate_value,
                    'percentage': immediate_percentage,
                    'count': len(immediate_risk)
                },
                'short_term_risk': {
                    'items': short_term_risk,
                    'value': short_term_value,
                    'percentage': short_term_percentage,
                    'count': len(short_term_risk)
                },
                'medium_term_risk': {
                    'items': medium_term_risk,
                    'value': medium_term_value,
                    'percentage': medium_term_percentage,
                    'count': len(medium_term_risk)
                },
                'high_quantity_risk': {
                    'items': high_quantity_risk,
                    'value': high_quantity_value,
                    'percentage': high_quantity_percentage,
                    'count': len(high_quantity_risk)
                },
                'metrics': {
                    'total_value': total_value,
                    'total_value_at_risk': immediate_value + short_term_value + medium_term_value,
                    'risk_percentage': immediate_percentage + short_term_percentage + medium_term_percentage
                }
            }
            
            current_app.logger.info(f"Value at Risk Analysis completed - Immediate: {immediate_percentage:.1f}%, Short-term: {short_term_percentage:.1f}%, Medium-term: {medium_term_percentage:.1f}%")
            return result
            
        except Exception as e:
            current_app.logger.error(f"Error in Value at Risk analysis: {str(e)}")
            return {
                'immediate_risk': {'items': [], 'value': 0, 'percentage': 0, 'count': 0},
                'short_term_risk': {'items': [], 'value': 0, 'percentage': 0, 'count': 0},
                'medium_term_risk': {'items': [], 'value': 0, 'percentage': 0, 'count': 0},
                'high_quantity_risk': {'items': [], 'value': 0, 'percentage': 0, 'count': 0},
                'metrics': {
                    'total_value': 0,
                    'total_value_at_risk': 0,
                    'risk_percentage': 0
                }
            }
    
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
            
            # Calculate basic metrics
            total_items = len(items)
            expiring_items = len([item for item in items if item.status == STATUS_EXPIRING_SOON])
            expired_items = len([item for item in items if item.status == STATUS_EXPIRED])
            low_stock_items = len([item for item in items if (item.quantity or 0) < 10])
            
            # Calculate value metrics
            total_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items)
            expiring_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items if item.days_until_expiry is not None and 0 < item.days_until_expiry <= 7)
            
            # Calculate Value at Risk analysis
            var_analysis = self._calculate_value_at_risk(items)
            
            # Calculate industry-standard metrics
            inventory_metrics = {
                'stock_turnover': total_value / (total_items or 1),  # Average value per item
                'expiry_risk_score': (expiring_value / total_value * 100) if total_value > 0 else 0,
                'inventory_health': {
                    'stock_coverage': sum(1 for item in items if (item.quantity or 0) >= 10) / total_items * 100 if total_items > 0 else 0,
                    'expiry_ratio': expiring_items / total_items * 100 if total_items > 0 else 0,
                    'value_at_risk': expiring_value / total_value * 100 if total_value > 0 else 0
                },
                'value_at_risk_analysis': {
                    'immediate_risk': {
                        'value': var_analysis['immediate_risk']['value'],
                        'percentage': var_analysis['immediate_risk']['percentage'],
                        'count': var_analysis['immediate_risk']['count'],
                        'items': var_analysis['immediate_risk']['items']
                    },
                    'short_term_risk': {
                        'value': var_analysis['short_term_risk']['value'],
                        'percentage': var_analysis['short_term_risk']['percentage'],
                        'count': var_analysis['short_term_risk']['count'],
                        'items': var_analysis['short_term_risk']['items']
                    },
                    'medium_term_risk': {
                        'value': var_analysis['medium_term_risk']['value'],
                        'percentage': var_analysis['medium_term_risk']['percentage'],
                        'count': var_analysis['medium_term_risk']['count'],
                        'items': var_analysis['medium_term_risk']['items']
                    },
                    'high_quantity_risk': {
                        'value': var_analysis['high_quantity_risk']['value'],
                        'percentage': var_analysis['high_quantity_risk']['percentage'],
                        'count': var_analysis['high_quantity_risk']['count'],
                        'items': var_analysis['high_quantity_risk']['items']
                    },
                    'total_metrics': var_analysis['metrics']
                }
            }
            
            # Calculate risk scores for all items
            items_with_risk = []
            for item in items:
                risk_score = self._calculate_risk_score(item)
                items_with_risk.append({
                    'id': item.id,
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit': item.unit,
                    'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                    'days_until_expiry': item.days_until_expiry,
                    'location': item.location,
                    'batch_number': item.batch_number,
                    'value': (item.quantity or 0) * (item.cost_price or 0),
                    'risk_score': risk_score
                })
            
            # Sort items by risk score
            items_with_risk.sort(key=lambda x: x['risk_score'], reverse=True)
            
            current_app.logger.info(f"Calculated metrics - Total: {total_items}, Expiring: {expiring_items}, Expired: {expired_items}, Low Stock: {low_stock_items}")
            current_app.logger.info(f"Value metrics - Total: £{total_value:.2f}, Expiring: £{expiring_value:.2f}")
            current_app.logger.info(f"Inventory health - Coverage: {inventory_metrics['inventory_health']['stock_coverage']:.1f}%, Expiry: {inventory_metrics['inventory_health']['expiry_ratio']:.1f}%, Risk: {inventory_metrics['inventory_health']['value_at_risk']:.1f}%")
            
            # Calculate expiry risk metrics
            critical_items = [item for item in items if item.days_until_expiry is not None and 0 <= item.days_until_expiry <= 7 and (item.quantity or 0) > 10]
            high_value_expiring = [item for item in items if item.days_until_expiry is not None and 0 <= item.days_until_expiry <= 7 and (item.quantity or 0) * (item.cost_price or 0) > 1000]
            
            # Group items by expiry timeframes
            expiry_timeframes = {
                'next_week': [],
                'next_month': [],
                'next_quarter': []
            }
            
            current_date = datetime.now().date()
            next_month_start = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
            next_month_end = (next_month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            next_quarter_end = (current_date.replace(day=1) + timedelta(days=92)).replace(day=1) - timedelta(days=1)
            
            for item in items:
                if not item.expiry_date:
                    continue
                    
                expiry_date = item.expiry_date.date() if isinstance(item.expiry_date, datetime) else item.expiry_date
                days = item.days_until_expiry
                
                if days is None:
                    continue
                    
                if 0 < days <= 7:
                    expiry_timeframes['next_week'].append(item)
                elif next_month_start <= expiry_date <= next_month_end:
                    expiry_timeframes['next_month'].append(item)
                elif next_month_end < expiry_date <= next_quarter_end:
                    expiry_timeframes['next_quarter'].append(item)
            
            # Calculate historical comparison (last 7 days)
            last_week = datetime.now().date() - timedelta(days=7)
            last_week_report = Report.query.filter_by(user_id=user_id, date=last_week).first()
            
            # Calculate trends
            trends = {}
            if last_week_report:
                trends = {
                    'expiring_items_change': expiring_items - last_week_report.expiring_items,
                    'expired_items_change': expired_items - last_week_report.expired_items,
                    'low_stock_change': low_stock_items - last_week_report.low_stock_items,
                    'total_value_change': total_value - (last_week_report.total_value or 0)
                }
            
            # Calculate active items (only those marked as active)
            active_items = len([item for item in items if item.status == STATUS_ACTIVE])
            
            # Prepare detailed report data
            low_stock_items_list = [
                {
                    'id': item.id,
                    'name': item.name,
                    'quantity': item.quantity,
                    'unit': item.unit
                }
                for item in items if (item.quantity or 0) < 10
            ]
            report_data = {
                'summary': {
                    'total_items': total_items,
                    'active_items': active_items,
                    'expired_items': expired_items,
                    'expiring_items': expiring_items,
                    'low_stock_items': low_stock_items,
                    'low_stock_items_list': low_stock_items_list,
                    'critical_items': len(critical_items),
                    'high_value_expiring': len(high_value_expiring),
                    'total_value': total_value,
                    'expiring_value': expiring_value,
                    'inventory_metrics': inventory_metrics,
                    'trends': trends
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
                            'value': (item.quantity or 0) * (item.cost_price or 0),
                            'risk_score': self._calculate_risk_score(item)
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
                            'value': (item.quantity or 0) * (item.cost_price or 0),
                            'risk_score': self._calculate_risk_score(item)
                        }
                        for item in high_value_expiring
                    ],
                    'all_items': items_with_risk  # Include all items, not just high-risk ones
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
                                'value': (item.quantity or 0) * (item.cost_price or 0),
                                'risk_score': self._calculate_risk_score(item)
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
                                'value': (item.quantity or 0) * (item.cost_price or 0),
                                'risk_score': self._calculate_risk_score(item)
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
                                'value': (item.quantity or 0) * (item.cost_price or 0),
                                'risk_score': self._calculate_risk_score(item)
                            }
                            for item in expiry_timeframes['next_quarter']
                        ]
                    }
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
            
            # Create report
            try:
                report = Report(
                    date=current_date,
                    user_id=user_id,
                    total_items=total_items,
                    total_value=total_value,
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
                raise Exception(f"Could not save report: {str(e)}")
        except Exception as e:
            current_app.logger.error(f"Error generating report: {str(e)}")
            raise Exception(f"Could not generate report: {str(e)}")
    
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