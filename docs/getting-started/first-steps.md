# First Steps

Welcome to Expiry Tracker! This guide will help you get started with the application after installation and configuration.

## Prerequisites

Before starting, ensure you have:

- ✅ [Installation completed](./installation.md)
- ✅ [Configuration set up](./configuration.md)
- ✅ Application running (`python run.py`)
- ✅ Database initialized and migrated

## Getting Started

### 1. Access the Application

1. **Open your browser** and navigate to `http://localhost:5000`
2. **You should see** the Expiry Tracker homepage with:
   - Welcome message
   - "Get Started" and "Login" buttons
   - Feature overview

### 2. Create Your First Account

1. **Click "Get Started"** or navigate to `/auth/register`
2. **Fill in the registration form**:
   - Username (unique identifier)
   - Email address (for notifications)
   - Password (minimum 8 characters)
   - Confirm password
3. **Click "Create Account"**
4. **Check your email** for verification code
5. **Enter the verification code** to activate your account

### 3. Complete Email Verification

1. **Check your email** (including spam folder)
2. **Copy the verification code** from the email
3. **Enter the code** in the verification form
4. **Click "Verify Email"**
5. **You'll be redirected** to the login page

### 4. Log In to Your Account

1. **Enter your credentials**:
   - Username or email
   - Password
2. **Click "Login"**
3. **You'll be redirected** to your dashboard

## Dashboard Overview

After logging in, you'll see your **Dashboard** with:

### Key Metrics
- **Total Items**: Number of items in your inventory
- **Expiring Soon**: Items expiring within 30 days
- **Expired Items**: Items past their expiry date
- **Total Value**: Combined value of all active items

### Quick Actions
- **Add New Item**: Quick access to add inventory
- **View Reports**: Access to reports and data
- **Settings**: Configure your account and integrations

### Recent Activity
- **Latest notifications**
- **Recent item changes**
- **System updates**

## Adding Your First Item

### Method 1: Manual Entry

1. **Click "Add New Item"** from the dashboard
2. **Fill in the item details**:
   - **Name**: Product name (e.g., "Milk")
   - **Description**: Optional details (e.g., "Organic whole milk")
   - **Quantity**: Amount in stock (e.g., 5)
   - **Unit**: Unit of measurement (e.g., "liters")
   - **Selling Price**: Price per unit (e.g., 2.50)
   - **Cost Price**: Cost per unit (e.g., 1.80)
   - **Expiry Date**: When the item expires

3. **Click "Add Item"**

### Method 2: OCR Date Extraction

1. **Click "Add New Item"**
2. **Fill in basic details**
3. **For Expiry Date**:
   - Click "Upload Image"
   - Take a photo of the expiry date
   - The system will extract the date automatically
4. **Review and confirm** the extracted date
5. **Complete the form** and save

## Setting Up Notifications

### Email Notifications

1. **Go to Settings** (gear icon in navigation)
2. **Find "Notification Preferences"**
3. **Toggle "Email Notifications"** to enable
4. **Verify your email** if prompted
5. **Save settings**

### Notification Schedule

The system sends daily notifications at **9:11 PM BST** about:
- Inventory status updates

## Configuring Zoho Integration (Optional)

### Step 1: Get Zoho Credentials

1. **Go to Zoho Developer Console**
2. **Create a new client**
3. **Set redirect URI**: `http://localhost:5000/auth/zoho/callback`
4. **Copy Client ID and Client Secret**

### Step 2: Configure in Settings

1. **Go to Settings** → **Zoho Integration**
2. **Enter your credentials**:
   - Zoho Client ID
   - Zoho Client Secret
3. **Click "Save Credentials"**
4. **Click "Connect to Zoho"**
5. **Authorize the application**

### Step 3: Sync Inventory

1. **Go to Inventory page**
2. **Click "Sync with Zoho"**
3. **Review imported items**
4. **Confirm synchronization**

## Exploring Features

### Reports and Reports

The Reports section provides:
- **Daily Reports**: Generate inventory status reports
- **Historical Data**: View past reports and trends
- **Risk Assessment**: Identify items requiring attention
- **Value Tracking**: Monitor total inventory value

### Key Features Overview

- **Inventory Management**: Add, edit, and delete items
- **OCR Date Extraction**: Upload images to extract expiry dates
- **Email Notifications**: Receive alerts for expiring items
- **In-app Notifications**: View notifications within the system
- **Daily Reports**: Generate and view inventory reports
- **Zoho Integration**: Sync with Zoho Inventory (if configured)
- **Activity Tracking**: Monitor all system activities
- **Security Features**: Enhanced security for sensitive operations

## Best Practices

### Item Management

1. **Use descriptive names** for easy searching
2. **Set accurate expiry dates** for proper tracking
3. **Include batch numbers** for traceability
4. **Use consistent units** across similar items
5. **Update quantities** regularly

### Notifications

1. **Enable email notifications** for important alerts
2. **Check notifications** regularly
3. **Act on expiry alerts** promptly
4. **Review daily reports** for trends

## Troubleshooting

### Common Issues

**Can't log in?**
- Check username/email spelling
- Verify password is correct
- Ensure email is verified
- Check if account is locked (too many failed attempts)

**Notifications not working?**
- Verify email is confirmed
- Check notification settings
- Ensure email service is configured
- Check spam folder

**OCR not extracting dates?**
- Ensure image is clear and well-lit
- Check date format is standard
- Verify Azure credentials are set
- Try manual entry as fallback

**Zoho sync issues?**
- Verify credentials are correct
- Check redirect URI matches
- Ensure proper scopes are set
- Check Zoho service status

## Next Steps

Now that you're set up, explore:

1. **[Inventory Management](../user-guide/inventory.md)** - Detailed guide to managing items
2. **[Reports](../user-guide/reports.md)** - Understanding reports and data
3. **[Settings](../user-guide/settings.md)** - Advanced configuration options
4. **[API Documentation](../api/README.md)** - For developers and integrations

## Support

If you encounter issues:

1. **Check this documentation** for solutions
2. **Review troubleshooting guides**
3. **Check application logs** for error details
4. **Contact support** with specific error messages

---

**Previous**: [Configuration Guide](./configuration.md) | **Next**: [Dashboard Overview](../user-guide/dashboard.md) 