# Dashboard Overview

The Dashboard is your central command center for managing inventory. It provides comprehensive insights and overview of your inventory status.

## Dashboard Layout

### Header Section
- **Navigation Menu**: Access to all major sections
- **User Profile**: Account settings and logout
- **Notifications Bell**: Quick access to recent notifications

### Main Dashboard Content

#### 1. Key Metrics Cards

**Total Items**
- Shows the total number of items in your inventory
- Color-coded based on status distribution
- Click to view detailed breakdown

**Expiring Soon**
- Items expiring within 30 days
- Red indicator for urgent items (≤7 days)
- Yellow indicator for items expiring soon (8-30 days)

**Expired Items**
- Items past their expiry date
- Red indicator with count
- Click to view and manage expired items

**Total Value**
- Combined value of all active items
- Calculated as: Quantity × Selling Price
- Updated on page refresh

#### 3. Recent Activity Feed

**Latest Notifications**
- Email notifications sent
- System alerts and updates
- Status changes

**Recent Item Changes**
- Items added, updated, or deleted
- Quantity modifications
- Status updates

**User Activities**
- Login/logout events
- Settings changes
- Integration activities

## Dashboard Features

### Status Updates

The dashboard updates to show:
- **Current inventory counts**
- **Current expiry status**
- **Value calculations**
- **Recent activity feed**

## Dashboard Metrics Explained

### Item Status Categories

**Active Items**
- Items in good condition
- Not expired or expiring soon
- Green status indicator

**Expiring Soon**
- Items expiring within 30 days
- Subdivided into:
  - **Warning** (≤7 days): Red indicator

**Expired Items**
- Items past expiry date
- Red status indicator
- Scheduled for cleanup

### Value Calculations

**Total Value**
- Sum of all active item values
- Formula: Σ(Quantity × Selling Price)
- Excludes expired items

**Expiring Value**
- Value of items expiring within 7 days
- Helps assess potential losses
- Risk management metric

**Expired Value**
- Value of expired items
- Historical loss tracking
- Cleanup planning

## Troubleshooting Dashboard

### Common Issues

**Metrics Not Updating**
- Check internet connection
- Refresh the page
- Clear browser cache
- Check application logs

**Missing Data**
- Verify database connection
- Check user permissions
- Review data filters
- Contact administrator

---

**Previous**: [First Steps](../getting-started/first-steps.md) | **Next**: [Inventory Management](./inventory.md) 