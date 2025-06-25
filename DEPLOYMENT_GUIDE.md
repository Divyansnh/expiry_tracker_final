# 🚀 Demo Deployment Guide - Expiry Tracker

This guide will help you deploy your full-featured Expiry Tracker demo to Render for portfolio showcase.

## 📋 Prerequisites

Before deploying, ensure you have:

1. **GitHub Repository**: Your code is pushed to GitHub
2. **Render Account**: Sign up at [render.com](https://render.com)
3. **External Service Credentials**: (Optional but recommended for full demo)

## 🔧 External Services Setup

### 1. **Email Service (Gmail)**
- Enable 2-Factor Authentication on your Gmail account
- Generate an App Password:
  - Go to Google Account Settings → Security → 2-Step Verification → App passwords
  - Generate password for "Mail"
  - Use this password in `MAIL_PASSWORD`

### 2. **Azure Computer Vision (OCR)**
- Create Azure Computer Vision resource:
  - Go to [Azure Portal](https://portal.azure.com)
  - Create Computer Vision resource
  - Copy the endpoint URL and key
  - Set `AZURE_VISION_ENDPOINT` and `AZURE_VISION_KEY`

### 3. **Zoho Integration (Optional)**
- Create Zoho Developer account
- Create a new client in Zoho Developer Console
- Set redirect URI to your demo domain
- Copy Client ID and Client Secret

## 🌐 Deployment Steps

### Step 1: Connect to Render

1. **Sign up/Login to Render**
   - Go to [render.com](https://render.com)
   - Sign up with your GitHub account

2. **Create New Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Select the `demo-deploy` branch

### Step 2: Configure the Service

**Basic Settings:**
- **Name**: `expiry-tracker-demo`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn wsgi:app`

**Environment Variables:**
Set these in Render's Environment Variables section:

```bash
# Required
FLASK_ENV=production
SECRET_KEY=your-super-secure-secret-key-here

# Database (will be auto-configured by Render)
DATABASE_URL=postgresql://... (auto-generated)

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com

# Azure Computer Vision (for OCR)
AZURE_VISION_KEY=your-azure-vision-key
AZURE_VISION_ENDPOINT=https://your-resource.cognitiveservices.azure.com/

# Zoho Integration (optional)
ZOHO_CLIENT_ID=your-zoho-client-id
ZOHO_CLIENT_SECRET=your-zoho-client-secret
ZOHO_REDIRECT_URI=https://your-app-name.onrender.com/auth/zoho/callback
ZOHO_ORGANIZATION_ID=your-organization-id

# Security Settings
SESSION_COOKIE_SECURE=true
SESSION_COOKIE_HTTPONLY=true
SESSION_COOKIE_SAMESITE=Strict
```

### Step 3: Add PostgreSQL Database

1. **Create Database**
   - In Render dashboard, click "New +" → "PostgreSQL"
   - Name: `expiry-tracker-db`
   - Plan: Free (for demo)

2. **Link Database to Web Service**
   - Go back to your web service
   - In Environment Variables, add:
   - `DATABASE_URL` will be auto-populated

### Step 4: Deploy and Setup

1. **Deploy the Service**
   - Click "Create Web Service"
   - Render will build and deploy your app

2. **Run Database Migrations**
   - Once deployed, go to your service URL
   - The app will automatically run migrations

3. **Setup Demo Data**
   - The demo data script will run automatically during build
   - If not, you can run it manually via Render's shell

## 🔍 Post-Deployment Verification

### 1. **Test Basic Functionality**
- Visit your app URL
- Go to `/demo` to see demo information
- Test login with demo credentials

### 2. **Test Core Features**
- [ ] User registration and login
- [ ] Add/edit inventory items
- [ ] Expiry date tracking
- [ ] Search and filter functionality
- [ ] Dashboard statistics

### 3. **Test Advanced Features**
- [ ] Email notifications (if configured)
- [ ] OCR date extraction (if Azure configured)
- [ ] Zoho integration (if configured)
- [ ] Report generation
- [ ] API endpoints

### 4. **Demo Credentials**
```
Admin User:
- Username: demo_admin
- Email: admin@demo-expiry-tracker.com
- Password: demo123

Regular User:
- Username: demo_user
- Email: user@demo-expiry-tracker.com
- Password: demo123

Manager User:
- Username: demo_manager
- Email: manager@demo-expiry-tracker.com
- Password: demo123
```

## 🛠️ Troubleshooting

### Common Issues

1. **Build Fails**
   - Check requirements.txt has all dependencies
   - Verify Python version compatibility
   - Check build logs for specific errors

2. **Database Connection Error**
   - Verify DATABASE_URL is set correctly
   - Check if PostgreSQL service is running
   - Ensure database exists and is accessible

3. **Email Not Working**
   - Verify Gmail app password is correct
   - Check 2FA is enabled on Gmail
   - Verify SMTP settings

4. **External Services Not Working**
   - Check API keys are correct
   - Verify service endpoints are accessible
   - Check service quotas/limits

### Debug Commands

```bash
# Check application logs
# Available in Render dashboard

# Test database connection
flask db current

# Run migrations manually
flask db upgrade

# Setup demo data manually
python scripts/setup_full_demo.py
```

## 📊 Demo Features Checklist

### ✅ Core Features
- [ ] User Authentication & Authorization
- [ ] Inventory Management
- [ ] Expiry Date Tracking
- [ ] Category Management
- [ ] Search & Filter
- [ ] Dashboard Analytics

### ✅ Advanced Features
- [ ] Email Notifications
- [ ] OCR Date Extraction
- [ ] Zoho Integration
- [ ] Scheduled Tasks
- [ ] Activity Logging
- [ ] Report Generation

### ✅ Technical Features
- [ ] RESTful API
- [ ] Responsive Design
- [ ] Security Headers
- [ ] Error Handling
- [ ] Logging System
- [ ] Database Migrations

## 🔄 Updating the Demo

### To Update with New Features:

1. **Update Main Branch**
   ```bash
   git checkout main
   # Make your changes
   git add .
   git commit -m "Add new features"
   git push origin main
   ```

2. **Update Demo Branch**
   ```bash
   git checkout demo-deploy
   git merge main
   git push origin demo-deploy
   ```

3. **Redeploy**
   - Render will automatically redeploy when you push to demo-deploy branch

## 📈 Performance Optimization

### For Production Demo:

1. **Database Optimization**
   - Use connection pooling
   - Add database indexes
   - Optimize queries

2. **Caching**
   - Add Redis for session storage
   - Cache frequently accessed data
   - Use CDN for static files

3. **Monitoring**
   - Set up application monitoring
   - Monitor database performance
   - Track user interactions

## 🎯 Portfolio Enhancement

### Add to Your Portfolio:

1. **Demo URL**: Include your deployed app URL
2. **GitHub Repository**: Link to your main branch
3. **Technical Stack**: List all technologies used
4. **Features**: Highlight key functionalities
5. **Screenshots**: Add screenshots of key features
6. **Code Quality**: Mention clean code practices

### Sample Portfolio Description:

```
Expiry Tracker - Full-Stack Inventory Management System

A comprehensive web application for tracking inventory expiry dates with advanced features including OCR date extraction, email notifications, and third-party integrations.

Technologies: Flask, PostgreSQL, SQLAlchemy, Bootstrap, Azure Computer Vision, Zoho API, Gmail SMTP

Features: User authentication, inventory management, expiry tracking, OCR, email notifications, reporting, RESTful API

Live Demo: [Your Render URL]
GitHub: [Your Repository URL]
```

## 🚨 Security Notes

1. **Never commit sensitive data** to Git
2. **Use environment variables** for all secrets
3. **Regularly update dependencies**
4. **Monitor for security vulnerabilities**
5. **Use HTTPS** in production
6. **Implement rate limiting** for API endpoints

## 📞 Support

If you encounter issues:

1. Check Render's documentation
2. Review application logs
3. Test locally first
4. Check environment variables
5. Verify external service credentials

---

**Happy Deploying! 🎉** 