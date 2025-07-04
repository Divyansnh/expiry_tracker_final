from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.core.extensions import db, login_manager
from app.models.user import User
from app.services.zoho_service import ZohoService
from app.services.email_service import EmailService
from app.services.activity_service import ActivityService
from datetime import datetime, timedelta
from app.forms.reset_password_request_form import ResetPasswordRequestForm
from app.forms.reset_password_form import ResetPasswordForm
from app.forms.login_form import LoginForm
from app.forms.verify_email_form import VerifyEmailForm

auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(int(user_id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        current_app.logger.info(f"Login attempt for email: {email}")
        
        user = User.query.filter_by(email=email).first()
        if not user:
            current_app.logger.warning(f"Login failed: User not found for email {email}")
            flash('Invalid email or password', 'danger')
            return render_template('auth/login.html', title='Login', form=form)

        # Check if account is locked
        if user.is_locked():
            remaining_time = user.get_lockout_time_remaining()
            if remaining_time:
                minutes = int(remaining_time.total_seconds() / 60)
                flash(f'Account is locked. Please try again in {minutes} minutes.', 'danger')
                return render_template('auth/login.html', title='Login', form=form)
        
        # Check if user is verified BEFORE checking password
        if not user.is_verified:
            current_app.logger.info(f"Unverified user {user.email} attempting to login")
            # Store email in session for verification
            session['pending_verification_email'] = user.email
            # Generate and send new verification code
            email_service = EmailService()
            if email_service.send_verification_email(user):
                current_app.logger.info(f"Verification email sent to {user.email}")
                flash('Please verify your email address to continue. A new verification code has been sent.', 'warning')
            else:
                current_app.logger.error(f"Failed to send verification email to {user.email}")
                flash('Please verify your email address. Error sending verification email.', 'error')
            return redirect(url_for('auth.verify_email'))
            
        # Only check password if user is verified
        if not user.verify_password(form.password.data):
            current_app.logger.warning(f"Login failed: Invalid password for user {user.username}")
            # Increment login attempts
            user.login_attempts += 1
            if user.login_attempts >= current_app.config['MAX_LOGIN_ATTEMPTS']:
                user.locked_until = datetime.utcnow() + current_app.config['LOGIN_LOCKOUT_DURATION']
                flash(f'Too many failed attempts. Account locked for {current_app.config["LOGIN_LOCKOUT_DURATION"].total_seconds() / 60} minutes.', 'danger')
            else:
                remaining_attempts = current_app.config['MAX_LOGIN_ATTEMPTS'] - user.login_attempts
                flash(f'Invalid email or password. {remaining_attempts} attempts remaining.', 'danger')
            db.session.commit()
            return render_template('auth/login.html', title='Login', form=form)
            
        current_app.logger.info(f"User found: {user.username}, is_verified: {user.is_verified}")
        
        # Reset login attempts on successful login
        user.login_attempts = 0
        user.locked_until = None
        
        # Set session to permanent if remember me is checked
        if form.remember_me.data:
            session.permanent = True
            current_app.permanent_session_lifetime = timedelta(hours=24)
        
        # Login user and set session cookie
        login_user(user, remember=form.remember_me.data)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        # Log successful login activity
        activity_service = ActivityService()
        activity_service.log_login(user.id)
        
        # Get the next URL from the query parameters
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.index')
            
        return redirect(next_page)
        
    return render_template('auth/login.html', title='Login', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register a new user."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        try:
            # Get form data
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            # Validate form data
            if not all([username, email, password, confirm_password]):
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'All fields are required.'}), 400
                flash('All fields are required.', 'error')
                return render_template('auth/register.html')
            
            if password != confirm_password:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Passwords do not match.'}), 400
                flash('Passwords do not match.', 'error')
                return render_template('auth/register.html')
            
            # Check if user already exists
            if User.query.filter_by(username=username).first():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Username already taken.'}), 400
                flash('Username already taken.', 'error')
                return render_template('auth/register.html')
            
            if User.query.filter_by(email=email).first():
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': 'Email already registered.'}), 400
                flash('Email already registered.', 'error')
                return render_template('auth/register.html')
            
            # Create new user
            user = User()
            user.username = username
            user.email = email
            try:
                user.password = password  # This will validate password strength
            except ValueError as e:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({'success': False, 'message': str(e)}), 400
                flash(str(e), 'error')
                return render_template('auth/register.html')
            
            # Generate verification token
            user.generate_verification_code()
            
            # Save user
            user.save()
            
            # Send verification email
            try:
                email_service = EmailService()
                if email_service.send_verification_email(user):
                    # Store email in session for verification
                    session['pending_verification_email'] = user.email
                    session.modified = True  # Ensure session is saved
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'success': True, 
                            'message': 'Registration successful! Please check your email to verify your account.',
                            'redirect': url_for('auth.verify_email')
                        })
                    flash('Registration successful! Please check your email to verify your account.', 'success')
                else:
                    current_app.logger.error(f"Failed to send verification email to {user.email}")
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return jsonify({
                            'success': True,
                            'message': 'Registration successful but verification email could not be sent. Please try resending the verification email.',
                            'redirect': url_for('auth.verify_email')
                        })
                    flash('Registration successful but verification email could not be sent. Please try resending the verification email.', 'warning')
            except Exception as e:
                current_app.logger.error(f"Error sending verification email: {str(e)}")
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': True,
                        'message': 'Registration successful but verification email could not be sent. Please try resending the verification email.',
                        'redirect': url_for('auth.verify_email')
                    })
                flash('Registration successful but verification email could not be sent. Please try resending the verification email.', 'warning')
            
            return redirect(url_for('auth.verify_email'))
            
        except Exception as e:
            current_app.logger.error(f"Error during registration: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': 'An error occurred during registration. Please try again.'}), 500
            flash('An error occurred during registration. Please try again.', 'error')
            return render_template('auth/register.html')
    
    return render_template('auth/register.html')

@auth_bp.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    """Email verification."""
    if current_user.is_authenticated and current_user.is_verified:
        return redirect(url_for('main.dashboard'))
        
    form = VerifyEmailForm()
    
    # Get the email from session
    email = session.get('pending_verification_email')
    if not email and current_user.is_authenticated:
        email = current_user.email
        # Update session with the email
        session['pending_verification_email'] = email
        session.modified = True
    
    if not email:
        flash('Email not found. Please try logging in again.', 'error')
        return redirect(url_for('auth.login'))
        
    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found. Please try registering again.', 'error')
            return redirect(url_for('auth.register'))
            
        if user.verify_code(form.verification_code.data):
            # Clear the session after successful verification
            session.pop('pending_verification_email', None)
            session.modified = True
            flash('Email verified successfully', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Invalid verification code', 'error')
            
    return render_template('auth/verify_email.html', form=form)

@auth_bp.route('/resend-verification', methods=['GET', 'POST'])
def resend_verification():
    """Resend verification email."""
    # Get email from session
    email = session.get('pending_verification_email')
    if not email and current_user.is_authenticated:
        email = current_user.email
        # Update session with the email
        session['pending_verification_email'] = email
        session.modified = True
    
    if not email:
        flash('Email not found. Please try logging in again.', 'error')
        return redirect(url_for('auth.login'))
    
    user = User.query.filter_by(email=email).first()
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('auth.verify_email'))
        
    if user.is_verified:
        flash('Email already verified', 'info')
        return redirect(url_for('auth.login'))
        
    # Generate new verification code
    user.generate_verification_code()
    user.save()
    
    email_service = EmailService()
    if email_service.send_verification_email(user):
        flash('Verification email sent. Please check your inbox.', 'success')
    else:
        flash('Error sending verification email. Please try again.', 'error')
        
    return redirect(url_for('auth.verify_email'))

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    # Log logout activity before logging out
    activity_service = ActivityService()
    activity_service.log_logout(current_user.id)
    
    logout_user()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('auth.login'))

@auth_bp.route('/zoho/test-config')
@login_required
def zoho_test_config():
    """Test Zoho configuration for debugging."""
    if not current_user.is_authenticated:
        return jsonify({'error': 'Not authenticated'}), 401
    
    user = current_user._get_current_object()
    if not isinstance(user, User):
        return jsonify({'error': 'Invalid user session'}), 401
    
    zoho_service = ZohoService(user)
    
    config_info = {
        'user_id': user.id,
        'has_client_id': bool(zoho_service.client_id),
        'has_client_secret': bool(zoho_service.client_secret),
        'client_id_preview': zoho_service.client_id[:10] + '...' if zoho_service.client_id else None,
        'redirect_uri': zoho_service.redirect_uri,
        'accounts_url': zoho_service.accounts_url,
        'base_url': zoho_service.base_url,
        'auth_url': zoho_service.get_auth_url()
    }
    
    return jsonify(config_info)

@auth_bp.route('/zoho/auth')
@login_required
def zoho_auth():
    """Initiate Zoho OAuth flow."""
    if not current_user.is_authenticated:
        flash('Please log in first', 'error')
        return redirect(url_for('auth.login'))
        
    # Check if user has Zoho credentials (either plain text or encrypted)
    has_credentials = (
        (current_user.zoho_client_id and current_user.zoho_client_secret) or
        (current_user.zoho_client_id_hash and current_user.zoho_client_secret_hash)
    )
    
    if not has_credentials:
        flash('Please configure your Zoho client credentials in Settings first.', 'error')
        return redirect(url_for('main.settings'))
        
    user = current_user._get_current_object()
    if not isinstance(user, User):
        flash('Invalid user session', 'error')
        return redirect(url_for('auth.login'))
        
    zoho_service = ZohoService(user)
    auth_url = zoho_service.get_auth_url()
    
    # Add debugging information
    current_app.logger.info(f"Zoho OAuth initiated for user {user.id}")
    current_app.logger.info(f"Redirect URI: {current_app.config['ZOHO_REDIRECT_URI']}")
    current_app.logger.info(f"Client ID: {zoho_service.client_id[:10]}..." if zoho_service.client_id else "No client ID")
    current_app.logger.info(f"Auth URL generated: {auth_url}")
    
    return redirect(auth_url)

@auth_bp.route('/zoho/callback')
@login_required
def zoho_callback():
    """Handle Zoho OAuth callback"""
    if not current_user.is_authenticated:
        flash('Please log in first', 'error')
        return redirect(url_for('auth.login'))
        
    code = request.args.get('code')
    error = request.args.get('error')
    error_description = request.args.get('error_description')
    
    # Add debugging for callback
    current_app.logger.info(f"Zoho callback received - User: {current_user.id}")
    current_app.logger.info(f"Code present: {bool(code)}")
    current_app.logger.info(f"Error: {error}")
    current_app.logger.info(f"Error description: {error_description}")
    
    if error:
        current_app.logger.error(f"Zoho OAuth error: {error} - {error_description}")
        flash(f'Zoho authorization failed: {error_description or error}', 'error')
        return redirect(url_for('main.settings'))
    
    if not code:
        current_app.logger.error("No authorization code received from Zoho")
        flash('No authorization code received from Zoho', 'error')
        return redirect(url_for('main.settings'))
    
    user = current_user._get_current_object()
    if not isinstance(user, User):
        flash('Invalid user session', 'error')
        return redirect(url_for('auth.login'))
        
    zoho_service = ZohoService(user)
    if zoho_service.handle_callback(code):
        flash('Successfully connected to Zoho! Your inventory will be synced when you visit the inventory page.', 'success')
    else:
        flash('Failed to connect to Zoho. Please try again.', 'error')
    
    return redirect(url_for('main.settings'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password request."""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
        
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        current_app.logger.info(f"Password reset requested for email: {form.email.data}")
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            current_app.logger.info(f"User found: {user.username}")
            # Invalidate any existing reset tokens
            user.clear_password_reset_token()
            # Generate new token
            token = user.generate_password_reset_token()
            current_app.logger.info(f"Generated reset token: {token[:20]}...")
            user.password_reset_token = token
            db.session.commit()
            
            # Send reset email
            email_service = EmailService()
            reset_url = url_for('auth.reset_password', token=token, _external=True)
            current_app.logger.info(f"Generated reset URL: {reset_url}")
            try:
                success = email_service.send_password_reset_email(user.email, reset_url)
                current_app.logger.info(f"Email send result: {success}")
                if not success:
                    current_app.logger.error("Failed to send password reset email")
            except Exception as e:
                current_app.logger.error(f"Error sending password reset email: {str(e)}", exc_info=True)
            
            # Always show the same message regardless of whether the email exists
            flash('If an account exists with this email, you will receive password reset instructions.')
            return redirect(url_for('auth.login'))
        else:
            current_app.logger.warning(f"No user found with email: {form.email.data}")
            # Don't reveal whether the email exists
            flash('If an account exists with this email, you will receive password reset instructions.')
            return redirect(url_for('auth.login'))
            
    return render_template('auth/forgot_password.html', form=form)

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        flash('You are already logged in. Please log out to reset your password.', 'info')
        return redirect(url_for('main.dashboard'))
        
    # Find user by token
    user = User.query.filter_by(password_reset_token=token).first()
    if not user:
        flash('Invalid or expired password reset link', 'danger')
        return redirect(url_for('auth.login'))
        
    # Verify the token
    if not user.verify_password_reset_token(token):
        flash('Invalid or expired password reset link', 'danger')
        return redirect(url_for('auth.login'))
        
    form = ResetPasswordForm()
    if form.validate_on_submit():
        try:
            user.password = form.password.data
            user.clear_password_reset_token()  # Clear the token after successful password reset
            db.session.commit()
            
            # Send confirmation email
            email_service = EmailService()
            if email_service.send_password_reset_confirmation(user.email):
                current_app.logger.info(f"Password reset confirmation email sent to {user.email}")
            else:
                current_app.logger.error(f"Failed to send password reset confirmation email to {user.email}")
                
            flash('Your password has been reset. Please log in with your new password.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'danger')
            return render_template('auth/reset_password.html', form=form, token=token)
            
    return render_template('auth/reset_password.html', form=form, token=token) 