# Inventory Management

## Overview

The Inventory Management module is the core feature of Expiry Tracker, allowing you to efficiently manage your inventory items, track expiry dates, and maintain accurate stock levels.

## Getting Started

### Accessing Inventory Management

1. **Login** to your Expiry Tracker account
2. **Navigate** to the "Inventory" section from the main navigation
3. **View** your current inventory items in the main dashboard

### Dashboard Overview

The inventory dashboard provides a comprehensive view of your inventory:

- **Total Items**: Complete count of all inventory items
- **Active Items**: Items that are in good condition and not expiring soon
- **Expiring Soon**: Items that will expire within 30 days
- **Expired Items**: Items that have passed their expiry date

## Adding New Items

### Method 1: Manual Entry

1. **Click** the "Add New Item" button
2. **Fill** in the required information:
   - **Name**: Product name (required)
   - **Description**: Product description (optional)
   - **Quantity**: Current stock quantity (required)
   - **Unit**: Unit of measurement (required)
   - **Expiry Date**: Expiry date (required)
   - **Selling Price**: Current selling price (optional)
   - **Cost Price**: Cost price for inventory valuation (optional)
   - **Discounted Price**: Special discounted price (optional)
   - **Batch Number**: Optional batch tracking (optional)
   - **Location**: Storage location (optional)
   - **Notes**: Additional notes (optional)

3. **Click** "Save Item" to add the item to your inventory

### Method 2: Image Upload with OCR

1. **Click** "Add New Item"
2. **Upload** an image containing the expiry date
3. **Click** "Extract Date" to automatically extract the expiry date
4. **Verify** the extracted date
5. **Complete** the remaining fields
6. **Save** the item

**Supported Image Formats:**
- JPEG (.jpg, .jpeg)
- PNG (.png)

**OCR Tips:**
- Ensure the date is clearly visible in the image
- Use good lighting for better accuracy
- Avoid blurry or low-resolution images
- The date should be in a standard format (DD/MM/YYYY, MM/DD/YYYY, etc.)

## Managing Existing Items

### Viewing Items

The inventory page displays all your items in a table format with:

- **Item Name**: Product name with description
- **Quantity**: Current stock level with unit
- **Expiry Date**: Days until expiry
- **Status**: Visual status indicator
- **Value**: Item value
- **Actions**: Edit, delete, and view options

### Editing Items

1. **Click** the "Edit" button next to any item
2. **Modify** the desired fields
3. **Click** "Update Item" to save changes

**Note**: Changes are automatically tracked in the activity log.

### Deleting Items

1. **Click** the "Delete" button next to an item
2. **Confirm** the deletion in the popup dialog
3. **Item** will be permanently removed from inventory

### Bulk Operations

#### Bulk Delete

1. **Select** multiple items using checkboxes
2. **Click** "Delete Selected" button
3. **Review** the items to be deleted
4. **Confirm** the bulk deletion
5. **Items** will be permanently removed from inventory

## Search and Filtering

### Search Functionality

Use the search bar to find items by:
- **Name**: Product name
- **Description**: Product description

### Filter Options

#### Status Filter
- **All**: Show all items
- **Active**: Items in good condition
- **Expired**: Items past expiry date
- **Expiring Soon**: Items expiring within 30 days
- **Pending**: Items without expiry dates

### Sorting Options

Items are automatically sorted by:
- **Expiry Date**: Days until expiry (ascending)

## Item Status System

### Status Indicators

The system automatically categorizes items based on their expiry dates:

#### 🟢 Active
- Items with more than 30 days until expiry
- Normal stock levels
- No immediate action required

#### 🟡 Expiring Soon
- Items expiring within 30 days
- Requires attention and planning
- Consider using or selling soon

#### 🔴 Expired
- Items past their expiry date
- Should be removed from inventory
- May need disposal or return

#### ⚪ Pending
- Items without expiry dates set
- Requires manual expiry date entry
- Temporary status until date is added

### Status Updates

Item status is automatically updated:
- **On page load**: When viewing inventory
- **Manual**: When editing items

## Best Practices

### Data Entry

1. **Be Consistent**: Use standard units and naming conventions
2. **Include Details**: Add descriptions and notes for better tracking
3. **Set Realistic Expiry Dates**: Use actual expiry dates, not best-before dates
4. **Update Regularly**: Keep quantities and dates current

### Organization

1. **Use Batch Numbers**: Track items by batch for better traceability
2. **Assign Locations**: Use location field to organize storage
3. **Regular Audits**: Periodically verify inventory accuracy
4. **Clean Up**: Remove expired items promptly

### Optimization

1. **Monitor Expiring Items**: Plan usage of items expiring soon
2. **Track Usage Patterns**: Identify frequently used items
3. **Use Bulk Operations**: Efficiently manage multiple items
4. **Regular Reviews**: Analyze inventory reports regularly

## Troubleshooting

### Common Issues

#### Item Not Saving
- **Check Required Fields**: Ensure all required fields are filled
- **Validate Data**: Check for invalid characters or formats
- **Refresh Page**: Try refreshing if the page seems unresponsive

#### OCR Not Working
- **Image Quality**: Ensure the image is clear and well-lit
- **Date Format**: Make sure the date is in a recognizable format
- **File Size**: Check that the image file is not too large
- **Try Manual Entry**: If OCR fails, enter the date manually

#### Search Not Finding Items
- **Check Spelling**: Verify the search term spelling
- **Clear Filters**: Ensure no filters are restricting results
- **Try Partial Search**: Use partial names or descriptions

### Getting Help

If you encounter issues:

1. **Check This Documentation**: Review troubleshooting sections
2. **Review Activity Log**: Check recent changes and actions
3. **Contact Support**: Reach out to the development team

## Integration Features

### Zoho Integration

If you have Zoho Inventory connected:

1. **Automatic Sync**: Items sync between systems
2. **Bidirectional Updates**: Changes reflect in both systems
3. **Conflict Resolution**: System handles conflicting data
4. **Manual Sync**: Force sync when needed

---

**Previous**: [Dashboard Overview](./dashboard.md) | **Next**: [Notifications](./notifications.md)

**Last Updated**: June 2025  
**Version**: 1.0.0 