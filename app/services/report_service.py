from datetime import datetime, timedelta, date
import secrets
from typing import Dict, List, Optional, Any
from flask import current_app
from app.core.extensions import db
from app.models.report import Report
from app.models.item import Item, STATUS_ACTIVE, STATUS_EXPIRING_SOON, STATUS_EXPIRED, STATUS_PENDING
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
        if not item.expiry_date:
            return 50  # Items without expiry dates get medium risk score
            
        score = 0
        quantity = item.quantity or 0
        value = quantity * (item.cost_price or 0)
        
        # 1. Expiry Risk (40% weight) - Use actual Item model logic
        days_until_expiry = item.days_until_expiry
        
        if days_until_expiry is None:
            score += 40  # Can't calculate, assume high risk
        elif days_until_expiry < 0:
            score += 40  # Expired items get maximum risk score
        elif 0 <= days_until_expiry <= 7:
            score += 40  # Critical: Within 7 days (matches STATUS_EXPIRING_SOON logic)
        elif 8 <= days_until_expiry <= 30:
            score += 25  # High: Within 30 days
        elif 31 <= days_until_expiry <= 90:
            score += 15  # Medium: Within 3 months
        elif 91 <= days_until_expiry <= 365:
            score += 5   # Low: Within 1 year
            
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
        if value > 1000:
            score += 30  # High value items
        elif value > 500:
            score += 20  # Medium value items
        elif value > 100:
            score += 10  # Low value items
            
        return min(score, 100)  # Cap at 100
    
    def _calculate_value_at_risk(self, items: List[Item]) -> Dict[str, Any]:
        """Calculate Value at Risk (VaR) analysis using industry-standard methodology.
        
        Categories:
        - Immediate Risk (0-7 days): Items expiring within a week
        - Short-term Risk (8-30 days): Items expiring within a month
        - Medium-term Risk (31-90 days): Items expiring within 3 months
        - High Quantity Risk: Items with large quantities expiring soon
        """
        total_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items)
        
        # Use actual Item model status and expiry logic
        immediate_risk_items = [item for item in items if item.status == STATUS_EXPIRING_SOON]
        short_term_items = [item for item in items if item.days_until_expiry is not None and 8 <= item.days_until_expiry <= 30]
        medium_term_items = [item for item in items if item.days_until_expiry is not None and 31 <= item.days_until_expiry <= 90]
        high_quantity_items = [item for item in items if (item.quantity or 0) > 100 and item.days_until_expiry is not None and item.days_until_expiry <= 30]
        
        # Calculate values
        immediate_risk_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in immediate_risk_items)
        short_term_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in short_term_items)
        medium_term_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in medium_term_items)
        high_quantity_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in high_quantity_items)
            
            # Calculate percentages
        immediate_risk_percentage = (immediate_risk_value / total_value * 100) if total_value > 0 else 0
        short_term_percentage = (short_term_value / total_value * 100) if total_value > 0 else 0
        medium_term_percentage = (medium_term_value / total_value * 100) if total_value > 0 else 0
        high_quantity_percentage = (high_quantity_value / total_value * 100) if total_value > 0 else 0
            
        # Prepare item details for each category
        immediate_risk_details = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                'days_until_expiry': item.days_until_expiry,
                'value': (item.quantity or 0) * (item.cost_price or 0),
                'status': item.status
            }
            for item in immediate_risk_items
        ]
        
        short_term_details = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                'days_until_expiry': item.days_until_expiry,
                'value': (item.quantity or 0) * (item.cost_price or 0),
                'status': item.status
            }
            for item in short_term_items
        ]
        
        medium_term_details = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                'days_until_expiry': item.days_until_expiry,
                'value': (item.quantity or 0) * (item.cost_price or 0),
                'status': item.status
            }
            for item in medium_term_items
        ]
        
        high_quantity_details = [
            {
                'id': item.id,
                'name': item.name,
                'quantity': item.quantity,
                'unit': item.unit,
                'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                'days_until_expiry': item.days_until_expiry,
                'value': (item.quantity or 0) * (item.cost_price or 0),
                'status': item.status
            }
            for item in high_quantity_items
        ]
        
        # Calculate overall risk metrics
        total_risk_value = immediate_risk_value + short_term_value + medium_term_value
        total_risk_percentage = (total_risk_value / total_value * 100) if total_value > 0 else 0
        
        # Risk score calculation (0-100)
        risk_score = min(100, (
            (immediate_risk_percentage * 0.4) +  # Immediate risk has highest weight
            (short_term_percentage * 0.3) +     # Short-term risk has medium weight
            (medium_term_percentage * 0.2) +    # Medium-term risk has lower weight
            (high_quantity_percentage * 0.1)    # High quantity risk has lowest weight
        ))
        
        return {
                'immediate_risk': {
                'value': immediate_risk_value,
                'percentage': immediate_risk_percentage,
                'count': len(immediate_risk_items),
                'items': immediate_risk_details
                },
                'short_term_risk': {
                    'value': short_term_value,
                    'percentage': short_term_percentage,
                'count': len(short_term_items),
                'items': short_term_details
                },
                'medium_term_risk': {
                    'value': medium_term_value,
                    'percentage': medium_term_percentage,
                'count': len(medium_term_items),
                'items': medium_term_details
                },
                'high_quantity_risk': {
                    'value': high_quantity_value,
                    'percentage': high_quantity_percentage,
                'count': len(high_quantity_items),
                'items': high_quantity_details
                },
                'metrics': {
                'total_risk_value': total_risk_value,
                'total_risk_percentage': total_risk_percentage,
                'risk_score': risk_score,
                'total_value': total_value
            }
        }
    
    def _generate_action_recommendations(self, items: List[Item], metrics: Dict, risk_analysis: Dict) -> List[Dict]:
        """Generate industry-aligned action recommendations based on inventory analysis.
        
        This method provides specific, actionable recommendations based on:
        - Industry best practices for inventory management
        - Risk assessment and mitigation strategies
        - Cost optimization opportunities
        - Operational efficiency improvements
        - Compliance and safety considerations
        """
        recommendations = []
        
        # Get key metrics
        total_items = len(items)
        total_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items)
        expiring_items = [item for item in items if item.days_until_expiry is not None and 0 < item.days_until_expiry <= 7]
        expired_items = [item for item in items if item.days_until_expiry is not None and item.days_until_expiry <= 0]
        low_stock_items = [item for item in items if (item.quantity or 0) < 10]
        high_value_items = [item for item in items if (item.quantity or 0) * (item.cost_price or 0) > 1000]
        
        # Calculate additional metrics
        stock_coverage = metrics.get('inventory_health', {}).get('stock_coverage', 0)
        expiry_ratio = metrics.get('inventory_health', {}).get('expiry_ratio', 0)
        value_at_risk = metrics.get('inventory_health', {}).get('value_at_risk', 0)
        
        # URGENT RECOMMENDATIONS (Immediate action required)
        
        # 1. Expired Items - Critical Safety Issue
        if expired_items:
            expired_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in expired_items)
            recommendations.append({
                'type': 'urgent',
                'category': 'safety_compliance',
                'title': 'Immediate Disposal Required',
                'message': f'Dispose of {len(expired_items)} expired items worth £{expired_value:.2f} immediately. Expired items pose safety risks and compliance issues.',
                'action': 'Review expired items list and arrange disposal within 24 hours',
                'impact': 'High - Safety and compliance risk',
                'effort': 'Medium',
                'item_ids': [item.id for item in expired_items],
                'priority_score': 100
            })
        
        # 2. Critical Expiry Risk
        if expiring_items:
            expiring_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in expiring_items)
            recommendations.append({
                'type': 'urgent',
                'category': 'expiry_management',
                'title': 'Critical Expiry Management',
                'message': f'Act immediately on {len(expiring_items)} items expiring within 7 days (value: £{expiring_value:.2f}). Consider discounting, donation, or disposal.',
                'action': 'Implement discount strategy or arrange disposal to minimize losses',
                'impact': 'High - Financial loss prevention',
                'effort': 'Medium',
                'item_ids': [item.id for item in expiring_items],
                'priority_score': 95
            })
        
        # 3. High Value at Risk
        if value_at_risk > 15:  # More than 15% of inventory value at risk
            recommendations.append({
                'type': 'urgent',
                'category': 'financial_risk',
                'title': 'High Financial Risk',
                'message': f'{value_at_risk:.1f}% of your inventory value (£{total_value * value_at_risk / 100:.2f}) is at risk of expiry. Implement aggressive discounting strategy.',
                'action': 'Review high-value expiring items and implement discounting or disposal strategy',
                'impact': 'High - Financial loss prevention',
                'effort': 'High',
                'item_ids': [item.id for item in high_value_items if item.days_until_expiry is not None and 0 < item.days_until_expiry <= 30],
                'priority_score': 90
            })
        
        # HIGH PRIORITY RECOMMENDATIONS (Action within 1 week)
        
        # 4. Low Stock Coverage
        if stock_coverage < 70:  # Less than 70% stock coverage
            recommendations.append({
                'type': 'high_priority',
                'category': 'stock_management',
                'title': 'Improve Stock Coverage',
                'message': f'Only {stock_coverage:.1f}% of items have adequate stock levels. Review reorder points and safety stock levels.',
                'action': 'Analyze demand patterns and adjust reorder points for low-stock items',
                'impact': 'Medium - Operational efficiency',
                'effort': 'Medium',
                'item_ids': [item.id for item in low_stock_items],
                'priority_score': 80
            })
        
        # 5. High Expiry Ratio
        if expiry_ratio > 20:  # More than 20% of items expiring soon
            recommendations.append({
                'type': 'high_priority',
                'category': 'procurement_optimization',
                'title': 'Optimize Procurement Strategy',
                'message': f'{expiry_ratio:.1f}% of inventory is expiring soon. Review ordering quantities and supplier lead times.',
                'action': 'Analyze ordering patterns and negotiate better terms with suppliers',
                'impact': 'Medium - Cost reduction',
                'effort': 'High',
                'item_ids': [item.id for item in items if item.days_until_expiry is not None and 0 < item.days_until_expiry <= 30],
                'priority_score': 75
            })
        
        # 6. Inventory Aging Analysis
        aging_items = [item for item in items if item.days_until_expiry is not None and 30 < item.days_until_expiry <= 90]
        if aging_items:
            aging_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in aging_items)
            recommendations.append({
                'type': 'high_priority',
                'category': 'inventory_optimization',
                'title': 'Address Aging Inventory',
                'message': f'{len(aging_items)} items (value: £{aging_value:.2f}) are aging (30-90 days). Consider promotional strategies.',
                'action': 'Implement promotional campaigns or bulk discounting for aging items',
                'impact': 'Medium - Cash flow improvement',
                'effort': 'Medium',
                'item_ids': [item.id for item in aging_items],
                'priority_score': 70
            })
        
        # MEDIUM PRIORITY RECOMMENDATIONS (Action within 1 month)
        
        # 7. Inventory Turnover Optimization
        if total_items > 0:
            avg_value_per_item = total_value / total_items
            if avg_value_per_item > 500:  # High average value per item
                recommendations.append({
                    'type': 'medium_priority',
                    'category': 'cost_optimization',
                    'title': 'Optimize High-Value Items',
                    'message': f'Average item value is £{avg_value_per_item:.2f}. Consider implementing ABC analysis for better inventory control.',
                    'action': 'Implement ABC analysis and adjust inventory policies for high-value items',
                    'impact': 'Medium - Cost optimization',
                    'effort': 'Medium',
                    'item_ids': [item.id for item in high_value_items],
                    'priority_score': 60
                })
        
        # 8. Safety Stock Review
        if low_stock_items:
            recommendations.append({
                'type': 'medium_priority',
                'category': 'risk_management',
                'title': 'Review Safety Stock Levels',
                'message': f'{len(low_stock_items)} items are below safety stock levels. Review and update safety stock calculations.',
                'action': 'Analyze demand variability and update safety stock levels',
                'impact': 'Medium - Risk reduction',
                'effort': 'Medium',
                'item_ids': [item.id for item in low_stock_items],
                'priority_score': 55
            })
        
        # 9. Supplier Performance Analysis
        if expiring_items:
            recommendations.append({
                'type': 'medium_priority',
                'category': 'supplier_management',
                'title': 'Evaluate Supplier Performance',
                'message': f'High expiry rates may indicate supplier issues. Review supplier performance and consider alternatives.',
                'action': 'Analyze supplier lead times and quality issues',
                'impact': 'Medium - Quality improvement',
                'effort': 'High',
                'item_ids': [item.id for item in expiring_items],
                'priority_score': 50
            })
        
        # STRATEGIC RECOMMENDATIONS (Long-term improvements)
        
        # 10. Technology Implementation
        if total_items > 50:  # Larger inventory
            recommendations.append({
                'type': 'strategic',
                'category': 'technology_upgrade',
                'title': 'Consider Inventory Management System',
                'message': f'With {total_items} items, consider implementing advanced inventory management features for better control.',
                'action': 'Evaluate inventory management software with forecasting capabilities',
                'impact': 'High - Long-term efficiency',
                'effort': 'High',
                'item_ids': [],
                'priority_score': 40
            })
        
        # 11. Process Optimization
        if expired_items or expiring_items:
            recommendations.append({
                'type': 'strategic',
                'category': 'process_improvement',
                'title': 'Implement FIFO/FEFO Processes',
                'message': 'High expiry rates suggest need for better stock rotation. Implement First-In-First-Out processes.',
                'action': 'Train staff on FIFO/FEFO procedures and update storage layout',
                'impact': 'Medium - Waste reduction',
                'effort': 'Medium',
                'item_ids': [item.id for item in items if item.expiry_date],
                'priority_score': 35
            })
        
        # 12. Performance Monitoring
        recommendations.append({
            'type': 'strategic',
            'category': 'performance_management',
            'title': 'Establish KPI Monitoring',
            'message': 'Implement regular monitoring of key performance indicators for continuous improvement.',
            'action': 'Set up weekly/monthly KPI reviews and action planning',
            'impact': 'Medium - Continuous improvement',
            'effort': 'Low',
            'item_ids': [],
            'priority_score': 30
        })
        
        # Sort recommendations by priority score (highest first)
        recommendations.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return recommendations
    
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
            
            # Calculate basic metrics using the actual Item model status constants
            total_items = len(items)
            expiring_items = len([item for item in items if item.status == STATUS_EXPIRING_SOON])
            expired_items = len([item for item in items if item.status == STATUS_EXPIRED])
            pending_items = len([item for item in items if item.status == STATUS_PENDING])
            active_items = len([item for item in items if item.status == STATUS_ACTIVE])
            low_stock_items = len([item for item in items if (item.quantity or 0) < 10])
            
            # Calculate value metrics
            total_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items)
            expiring_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items if item.status == STATUS_EXPIRING_SOON)
            expired_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items if item.status == STATUS_EXPIRED)
            
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
                    'risk_score': risk_score,
                    'status': item.status
                })
            
            # Sort items by risk score
            items_with_risk.sort(key=lambda x: x['risk_score'], reverse=True)
            
            current_app.logger.info(f"Calculated metrics - Total: {total_items}, Expiring: {expiring_items}, Expired: {expired_items}, Pending: {pending_items}, Active: {active_items}, Low Stock: {low_stock_items}")
            current_app.logger.info(f"Value metrics - Total: £{total_value:.2f}, Expiring: £{expiring_value:.2f}, Expired: £{expired_value:.2f}")
            current_app.logger.info(f"Inventory health - Coverage: {inventory_metrics['inventory_health']['stock_coverage']:.1f}%, Expiry: {inventory_metrics['inventory_health']['expiry_ratio']:.1f}%, Risk: {inventory_metrics['inventory_health']['value_at_risk']:.1f}%")
            
            # Calculate expiry risk metrics using actual status
            critical_items = [item for item in items if item.status == STATUS_EXPIRING_SOON and (item.quantity or 0) > 10]
            high_value_expiring = [item for item in items if item.status == STATUS_EXPIRING_SOON and (item.quantity or 0) * (item.cost_price or 0) > 1000]
            
            # Generate comprehensive expiry analysis
            comprehensive_expiry_analysis = self._generate_comprehensive_expiry_analysis(items)
            
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
            
            # Create items by status breakdown
            items_by_status = {
                'active': active_items,
                'expired': expired_items,
                'expiring_soon': expiring_items,
                'pending_expiry_date': pending_items
            }
            
            report_data = {
                'summary': {
                    'total_items': total_items,
                    'active_items': active_items,
                    'expired_items': expired_items,
                    'expiring_items': expiring_items,
                    'pending_items': pending_items,
                    'low_stock_items': low_stock_items,
                    'low_stock_items_list': low_stock_items_list,
                    'critical_items': len(critical_items),
                    'high_value_expiring': len(high_value_expiring),
                    'total_value': total_value,
                    'expiring_value': expiring_value,
                    'expired_value': expired_value,
                    'inventory_metrics': inventory_metrics,
                    'trends': trends,
                    'items_by_status': items_by_status
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
                            'risk_score': self._calculate_risk_score(item),
                            'status': item.status
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
                            'risk_score': self._calculate_risk_score(item),
                            'status': item.status
                        }
                        for item in high_value_expiring
                    ],
                    'all_items': items_with_risk  # Include all items, not just high-risk ones
                },
                'expiry_analysis': comprehensive_expiry_analysis,
                'action_recommendations': self._generate_action_recommendations(items, inventory_metrics, var_analysis['metrics'])
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
    
    def get_reports_by_date_range_paginated(self, start_date: date, end_date: date, user_id: int, page: int = 1, per_page: int = 20) -> tuple[List[Report], int]:
        """Get paginated reports within a date range for a specific user.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            user_id: The ID of the user to get reports for
            page: Page number (1-based)
            per_page: Number of reports per page
            
        Returns:
            Tuple of (reports, total_count)
        """
        try:
            query = Report.query.filter(
                Report.date >= start_date,
                Report.date <= end_date,
                Report.user_id == user_id
            )
            
            # Get total count
            total_count = query.count()
            
            # Get paginated results
            reports = query.order_by(Report.date.desc()).offset((page - 1) * per_page).limit(per_page).all()
            
            return reports, total_count
        except Exception as e:
            current_app.logger.error(f"Error getting paginated reports by date range: {str(e)}")
            return [], 0
    
    def get_all_reports_paginated(self, user_id: int, page: int = 1, per_page: int = 20) -> tuple[List[Report], int]:
        """Get all paginated reports for a specific user without date filtering.
        
        Args:
            user_id: The ID of the user to get reports for
            page: Page number (1-based)
            per_page: Number of reports per page
            
        Returns:
            Tuple of (reports, total_count)
        """
        try:
            query = Report.query.filter(Report.user_id == user_id)
            
            # Get total count
            total_count = query.count()
            
            # Get paginated results
            reports = query.order_by(Report.date.desc()).offset((page - 1) * per_page).limit(per_page).all()
            
            return reports, total_count
        except Exception as e:
            current_app.logger.error(f"Error getting all paginated reports: {str(e)}")
            return [], 0
    
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
    
    def _generate_comprehensive_expiry_analysis(self, items: List[Item]) -> Dict[str, Any]:
        """Generate comprehensive expiry analysis covering all items with proper categorization.
        
        Categories:
        - Expired: Items with days_until_expiry < 0
        - Critical: Items with days_until_expiry 0-7 (matches STATUS_EXPIRING_SOON)
        - Short-term: Items with days_until_expiry 8-30
        - Medium-term: Items with days_until_expiry 31-90
        - Long-term: Items with days_until_expiry 91-365
        - Beyond Year: Items with days_until_expiry > 365
        - No Expiry Date: Items without expiry_date
        """
        today = datetime.now().date()
        
        # Categorize items using actual Item model logic
        expired_items = [item for item in items if item.status == STATUS_EXPIRED]
        critical_items = [item for item in items if item.status == STATUS_EXPIRING_SOON]
        short_term_items = [item for item in items if item.days_until_expiry is not None and 8 <= item.days_until_expiry <= 30]
        medium_term_items = [item for item in items if item.days_until_expiry is not None and 31 <= item.days_until_expiry <= 90]
        long_term_items = [item for item in items if item.days_until_expiry is not None and 91 <= item.days_until_expiry <= 365]
        beyond_year_items = [item for item in items if item.days_until_expiry is not None and item.days_until_expiry > 365]
        no_expiry_items = [item for item in items if item.status == STATUS_PENDING]
        
        # Calculate metrics for each category
        categories = {
            'expired': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                        'days_until_expiry': item.days_until_expiry,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in expired_items
                ],
                'count': len(expired_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in expired_items),
                'total_quantity': sum(item.quantity or 0 for item in expired_items)
            },
            'critical': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                        'days_until_expiry': item.days_until_expiry,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in critical_items
                ],
                'count': len(critical_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in critical_items),
                'total_quantity': sum(item.quantity or 0 for item in critical_items)
            },
            'short_term': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                        'days_until_expiry': item.days_until_expiry,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in short_term_items
                ],
                'count': len(short_term_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in short_term_items),
                'total_quantity': sum(item.quantity or 0 for item in short_term_items)
            },
            'medium_term': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                        'days_until_expiry': item.days_until_expiry,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in medium_term_items
                ],
                'count': len(medium_term_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in medium_term_items),
                'total_quantity': sum(item.quantity or 0 for item in medium_term_items)
            },
            'long_term': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                        'days_until_expiry': item.days_until_expiry,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in long_term_items
                ],
                'count': len(long_term_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in long_term_items),
                'total_quantity': sum(item.quantity or 0 for item in long_term_items)
            },
            'beyond_year': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': item.expiry_date.strftime('%Y-%m-%d') if item.expiry_date else None,
                        'days_until_expiry': item.days_until_expiry,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in beyond_year_items
                ],
                'count': len(beyond_year_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in beyond_year_items),
                'total_quantity': sum(item.quantity or 0 for item in beyond_year_items)
            },
            'no_expiry_date': {
                'items': [
                    {
                        'id': item.id,
                        'name': item.name,
                        'quantity': item.quantity,
                        'unit': item.unit,
                        'expiry_date': None,
                        'days_until_expiry': None,
                        'value': (item.quantity or 0) * (item.cost_price or 0),
                        'status': item.status
                    }
                    for item in no_expiry_items
                ],
                'count': len(no_expiry_items),
                'total_value': sum((item.quantity or 0) * (item.cost_price or 0) for item in no_expiry_items),
                'total_quantity': sum(item.quantity or 0 for item in no_expiry_items)
            }
        }
        
        # Calculate overall metrics
        total_items = len(items)
        total_value = sum((item.quantity or 0) * (item.cost_price or 0) for item in items)
        
        # Calculate percentages
        overall_metrics = {
            'total_items': total_items,
            'total_value': total_value,
            'expired_percentage': (categories['expired']['count'] / total_items * 100) if total_items > 0 else 0,
            'expiring_soon_percentage': (categories['critical']['count'] / total_items * 100) if total_items > 0 else 0,
            'short_term_percentage': (categories['short_term']['count'] / total_items * 100) if total_items > 0 else 0,
            'medium_term_percentage': (categories['medium_term']['count'] / total_items * 100) if total_items > 0 else 0,
            'long_term_percentage': (categories['long_term']['count'] / total_items * 100) if total_items > 0 else 0,
            'beyond_year_percentage': (categories['beyond_year']['count'] / total_items * 100) if total_items > 0 else 0,
            'no_expiry_percentage': (categories['no_expiry_date']['count'] / total_items * 100) if total_items > 0 else 0,
            'value_at_risk_percentage': ((categories['expired']['total_value'] + categories['critical']['total_value']) / total_value * 100) if total_value > 0 else 0
        }
        
        current_app.logger.info(f"Comprehensive expiry analysis - Total: {total_items}, Expired: {categories['expired']['count']}, Critical: {categories['critical']['count']}, Short-term: {categories['short_term']['count']}, Medium-term: {categories['medium_term']['count']}, Long-term: {categories['long_term']['count']}, Beyond Year: {categories['beyond_year']['count']}, No Expiry: {categories['no_expiry_date']['count']}")
        
        return {
            'categories': categories,
            'overall_metrics': overall_metrics
        } 