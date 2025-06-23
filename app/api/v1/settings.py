import os
import random
import string
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from flask_login import login_required, current_user
from app.core.extensions import db
from app.models.user import User
from app.services.zoho_service import ZohoService, verify_zoho_credential
from app.utils.security import hash_zoho_credential
from app.api.v1.blueprint import api_bp
import logging
import secrets

# Configure logging for credential access
credential_logger = logging.getLogger('credential_access')
credential_logger.setLevel(logging.INFO)

# Create file handler for credential access logs
if not credential_logger.handlers:
    file_handler = logging.FileHandler('logs/credential_access.log')
    file_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    credential_logger.addHandler(file_handler)

# Rate limiting configuration
RATE_LIMIT_CONFIG = {
    'email_code_requests': {
        'max_attempts': 5,  # Maximum 5 email code requests
        'window_minutes': 15,  # Per 15 minutes
        'lockout_minutes': 30  # Lockout for 30 minutes after exceeding limit
    },
    'enhanced_disconnect_email_requests': {
        'max_attempts': 5,  # Maximum 5 enhanced disconnect email code requests (increased from 3)
        'window_minutes': 15,  # Per 15 minutes
        'lockout_minutes': 30  # Lockout for 30 minutes after exceeding limit
    },
    'report_deletion_email_requests': {
        'max_attempts': 3,  # Maximum 3 report deletion email code requests
        'window_minutes': 15,  # Per 15 minutes
        'lockout_minutes': 30  # Lockout for 30 minutes after exceeding limit
    },
    'verification_attempts': {
        'max_attempts': 5,  # Maximum 5 verification attempts
        'window_minutes': 15,  # Per 15 minutes
        'lockout_minutes': 60  # Lockout for 60 minutes after exceeding limit
    },
    'enhanced_disconnect_verification': {
        'max_attempts': 5,  # Maximum 5 enhanced disconnect verification attempts (increased from 3)
        'window_minutes': 15,  # Per 15 minutes
        'lockout_minutes': 60  # Lockout for 60 minutes after exceeding limit
    },
    'report_deletion_verification': {
        'max_attempts': 3,  # Maximum 3 report deletion verification attempts
        'window_minutes': 15,  # Per 15 minutes
        'lockout_minutes': 60  # Lockout for 60 minutes after exceeding limit
    }
}

# In-memory rate limiting storage (in production, use Redis or database)
rate_limit_store = {}

def check_rate_limit(user_id: int, action: str) -> dict:
    """Check if user has exceeded rate limits for a specific action."""
    current_time = datetime.utcnow()
    user_key = f"{user_id}_{action}"
    
    if user_key not in rate_limit_store:
        rate_limit_store[user_key] = {
            'attempts': [],
            'locked_until': None
        }
    
    user_data = rate_limit_store[user_key]
    config = RATE_LIMIT_CONFIG[action]
    
    # Check if user is currently locked out
    if user_data['locked_until'] and current_time < user_data['locked_until']:
        remaining_lockout = (user_data['locked_until'] - current_time).total_seconds() / 60
        return {
            'allowed': False,
            'reason': f'Rate limit exceeded. Try again in {int(remaining_lockout)} minutes.',
            'remaining_attempts': 0,
            'lockout_remaining': int(remaining_lockout)
        }
    
    # Clear expired attempts
    window_start = current_time - timedelta(minutes=config['window_minutes'])
    user_data['attempts'] = [attempt for attempt in user_data['attempts'] if attempt > window_start]
    
    # Check if user has exceeded the limit
    if len(user_data['attempts']) >= config['max_attempts']:
        # Set lockout period
        user_data['locked_until'] = current_time + timedelta(minutes=config['lockout_minutes'])
        return {
            'allowed': False,
            'reason': f'Rate limit exceeded. Try again in {config["lockout_minutes"]} minutes.',
            'remaining_attempts': 0,
            'lockout_remaining': config['lockout_minutes']
        }
    
    # Add current attempt
    user_data['attempts'].append(current_time)
    
    return {
        'allowed': True,
        'remaining_attempts': config['max_attempts'] - len(user_data['attempts']),
        'lockout_remaining': 0
    }

@api_bp.route('/settings/notifications', methods=['PUT'])
@login_required
def update_notification_settings():
    """Update notification preferences via API."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        email_notifications = data.get('email_notifications', False)
        current_user.email_notifications = email_notifications
        current_user.save()
        
        return jsonify({
            'message': 'Notification settings updated successfully',
            'email_notifications': current_user.email_notifications
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating notification settings: {str(e)}")
        return jsonify({'error': f'Error updating notification settings: {str(e)}'}), 500

@api_bp.route('/settings/zoho-credentials', methods=['PUT'])
@login_required
def update_zoho_credentials():
    """Update Zoho credentials via API."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        zoho_client_id = data.get('zoho_client_id')
        zoho_client_secret = data.get('zoho_client_secret')
        
        # Handle partial updates (when only one credential is provided)
        if zoho_client_id is not None and zoho_client_secret is not None:
            # Both credentials provided
            if not zoho_client_id.strip() or not zoho_client_secret.strip():
                return jsonify({'error': 'Both Zoho Client ID and Client Secret are required'}), 400
            
            # Check if these credentials are already being used by another user
            # Check plain text credentials first
            existing_user_with_client_id = User.query.filter(
                User.zoho_client_id == zoho_client_id.strip(),
                User.id != current_user.id
            ).first()
            
            if existing_user_with_client_id:
                return jsonify({'error': 'These Zoho credentials are already being used by another user. Please use different credentials.'}), 409
            
            existing_user_with_client_secret = User.query.filter(
                User.zoho_client_secret == zoho_client_secret.strip(),
                User.id != current_user.id
            ).first()
            
            if existing_user_with_client_secret:
                return jsonify({'error': 'These Zoho credentials are already being used by another user. Please use different credentials.'}), 409
            
            # Check encrypted credentials by attempting to decrypt and compare
            try:
                from app.utils.security import verify_zoho_credential
                
                # Get all users with encrypted credentials
                users_with_encrypted_creds = User.query.filter(
                    User.id != current_user.id
                ).all()
                
                # Filter users with encrypted credentials in Python
                users_with_encrypted_creds = [
                    user for user in users_with_encrypted_creds 
                    if user.zoho_client_id_hash or user.zoho_client_secret_hash
                ]
                
                for user in users_with_encrypted_creds:
                    # Check client ID
                    if user.zoho_client_id_hash and user.zoho_client_id_salt:
                        try:
                            decrypted_client_id = verify_zoho_credential(user.zoho_client_id_hash, user.zoho_client_id_salt)
                            if decrypted_client_id and decrypted_client_id.strip() == zoho_client_id.strip():
                                return jsonify({'error': 'These Zoho credentials are already being used by another user. Please use different credentials.'}), 409
                        except Exception as e:
                            current_app.logger.warning(f"Could not decrypt client ID for user {user.id}: {str(e)}")
                    
                    # Check client secret
                    if user.zoho_client_secret_hash and user.zoho_client_secret_salt:
                        try:
                            decrypted_client_secret = verify_zoho_credential(user.zoho_client_secret_hash, user.zoho_client_secret_salt)
                            if decrypted_client_secret and decrypted_client_secret.strip() == zoho_client_secret.strip():
                                return jsonify({'error': 'These Zoho credentials are already being used by another user. Please use different credentials.'}), 409
                        except Exception as e:
                            current_app.logger.warning(f"Could not decrypt client secret for user {user.id}: {str(e)}")
                            
            except Exception as e:
                current_app.logger.warning(f"Could not check encrypted credentials for uniqueness: {str(e)}")
                # Continue with the check, but log the warning
            
            # Encrypt both credentials using the new encryption system
            try:
                encrypted_client_id, client_id_salt = hash_zoho_credential(zoho_client_id)
                encrypted_client_secret, client_secret_salt = hash_zoho_credential(zoho_client_secret)
                
                current_user.zoho_client_id_hash = encrypted_client_id
                current_user.zoho_client_id_salt = client_id_salt
                current_user.zoho_client_secret_hash = encrypted_client_secret
                current_user.zoho_client_secret_salt = client_secret_salt
                
                # Clear plain text fields for security
                current_user.zoho_client_id = None
                current_user.zoho_client_secret = None
                
            except Exception as e:
                return jsonify({'error': f'Error encrypting credentials: {str(e)}'}), 500
                
        elif zoho_client_id is not None:
            # Only client ID provided
            if not zoho_client_id.strip():
                return jsonify({'error': 'Zoho Client ID cannot be empty'}), 400
            
            # Check if this client ID is already being used by another user
            existing_user_with_client_id = User.query.filter(
                User.zoho_client_id == zoho_client_id.strip(),
                User.id != current_user.id
            ).first()
            
            if existing_user_with_client_id:
                return jsonify({'error': 'This Zoho Client ID is already being used by another user. Please use a different Client ID.'}), 409
            
            # Check encrypted credentials for client ID
            try:
                from app.utils.security import verify_zoho_credential
                
                # Get all users with encrypted credentials
                users_with_encrypted_creds = User.query.filter(
                    User.id != current_user.id
                ).all()
                
                # Filter users with encrypted credentials in Python
                users_with_encrypted_creds = [
                    user for user in users_with_encrypted_creds 
                    if user.zoho_client_id_hash
                ]
                
                for user in users_with_encrypted_creds:
                    if user.zoho_client_id_hash and user.zoho_client_id_salt:
                        try:
                            decrypted_client_id = verify_zoho_credential(user.zoho_client_id_hash, user.zoho_client_id_salt)
                            if decrypted_client_id and decrypted_client_id.strip() == zoho_client_id.strip():
                                return jsonify({'error': 'This Zoho Client ID is already being used by another user. Please use a different Client ID.'}), 409
                        except Exception as e:
                            current_app.logger.warning(f"Could not decrypt client ID for user {user.id}: {str(e)}")
                            
            except Exception as e:
                current_app.logger.warning(f"Could not check encrypted client ID for uniqueness: {str(e)}")
            
            try:
                encrypted_client_id, client_id_salt = hash_zoho_credential(zoho_client_id)
                current_user.zoho_client_id_hash = encrypted_client_id
                current_user.zoho_client_id_salt = client_id_salt
                current_user.zoho_client_id = None  # Clear plain text
            except Exception as e:
                return jsonify({'error': f'Error encrypting client ID: {str(e)}'}), 500
                
        elif zoho_client_secret is not None:
            # Only client secret provided
            if not zoho_client_secret.strip():
                return jsonify({'error': 'Zoho Client Secret cannot be empty'}), 400
            
            # Check if this client secret is already being used by another user
            existing_user_with_client_secret = User.query.filter(
                User.zoho_client_secret == zoho_client_secret.strip(),
                User.id != current_user.id
            ).first()
            
            if existing_user_with_client_secret:
                return jsonify({'error': 'This Zoho Client Secret is already being used by another user. Please use a different Client Secret.'}), 409
            
            # Check encrypted credentials for client secret
            try:
                from app.utils.security import verify_zoho_credential
                
                # Get all users with encrypted credentials
                users_with_encrypted_creds = User.query.filter(
                    User.id != current_user.id
                ).all()
                
                # Filter users with encrypted credentials in Python
                users_with_encrypted_creds = [
                    user for user in users_with_encrypted_creds 
                    if user.zoho_client_secret_hash
                ]
                
                for user in users_with_encrypted_creds:
                    if user.zoho_client_secret_hash and user.zoho_client_secret_salt:
                        try:
                            decrypted_client_secret = verify_zoho_credential(user.zoho_client_secret_hash, user.zoho_client_secret_salt)
                            if decrypted_client_secret and decrypted_client_secret.strip() == zoho_client_secret.strip():
                                return jsonify({'error': 'This Zoho Client Secret is already being used by another user. Please use a different Client Secret.'}), 409
                        except Exception as e:
                            current_app.logger.warning(f"Could not decrypt client secret for user {user.id}: {str(e)}")
                            
            except Exception as e:
                current_app.logger.warning(f"Could not check encrypted client secret for uniqueness: {str(e)}")
            
            try:
                encrypted_client_secret, client_secret_salt = hash_zoho_credential(zoho_client_secret)
                current_user.zoho_client_secret_hash = encrypted_client_secret
                current_user.zoho_client_secret_salt = client_secret_salt
                current_user.zoho_client_secret = None  # Clear plain text
            except Exception as e:
                return jsonify({'error': f'Error encrypting client secret: {str(e)}'}), 500
        else:
            return jsonify({'error': 'At least one credential must be provided'}), 400
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Zoho credentials updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error updating Zoho credentials: {str(e)}")
        return jsonify({'error': f'Error updating Zoho credentials: {str(e)}'}), 500

@api_bp.route('/settings/disconnect-zoho', methods=['DELETE'])
@login_required
def disconnect_zoho():
    """Disconnect from Zoho via API."""
    try:
        # Clear Zoho tokens and credentials
        current_user.zoho_access_token = None
        current_user.zoho_refresh_token = None
        current_user.zoho_token_expires_at = None
        current_user.zoho_client_id = None
        current_user.zoho_client_secret = None
        current_user.zoho_client_id_hash = None
        current_user.zoho_client_secret_hash = None
        current_user.zoho_client_id_salt = None
        current_user.zoho_client_secret_salt = None
        
        db.session.commit()
        
        return jsonify({'message': 'Successfully disconnected from Zoho'})
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error disconnecting from Zoho: {str(e)}")
        return jsonify({'error': f'Error disconnecting from Zoho: {str(e)}'}), 500

@api_bp.route('/settings/verify-password-for-email-notification', methods=['POST'])
@login_required
def verify_password_for_email_notification():
    """Verify user password for email notification changes"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Add debugging information
        current_app.logger.info(f'Email notification verification attempt - User ID: {current_user.id}, Password length: {len(password) if password else 0}')
        
        # Verify password using the User model's verify_password method
        password_verified = current_user.verify_password(password)
        current_app.logger.info(f'Email notification password verification result: {password_verified}')
        
        if not password_verified:
            # Log failed attempt
            credential_logger.warning(f'Failed email notification verification attempt - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        # Log successful verification
        credential_logger.info(f'Successful email notification verification - User ID: {current_user.id}, IP: {request.remote_addr}')
        
        return jsonify({'success': True, 'message': 'Password verified successfully'})
        
    except Exception as e:
        credential_logger.error(f'Error in email notification password verification - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@api_bp.route('/settings/verify-password-for-disconnect', methods=['POST'])
@login_required
def verify_password_for_disconnect():
    """Verify user password for disconnect operation"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'success': False, 'error': 'Password is required'}), 400
        
        # Add debugging information
        current_app.logger.info(f'Disconnect verification attempt - User ID: {current_user.id}, Password length: {len(password) if password else 0}')
        
        # Verify password using the User model's verify_password method
        password_verified = current_user.verify_password(password)
        current_app.logger.info(f'Password verification result: {password_verified}')
        
        if not password_verified:
            # Log failed attempt
            credential_logger.warning(f'Failed disconnect verification attempt - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        # Log successful verification
        credential_logger.info(f'Successful disconnect verification - User ID: {current_user.id}, IP: {request.remote_addr}')
        
        return jsonify({'success': True, 'message': 'Password verified successfully'})
        
    except Exception as e:
        credential_logger.error(f'Error in disconnect password verification - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@api_bp.route('/settings/verify-password-for-credentials', methods=['POST'])
@login_required
def verify_password_for_credentials():
    """Verify user password for secure credential access"""
    try:
        data = request.get_json()
        password = data.get('password')
        credential_type = data.get('credential_type')
        
        if not password or not credential_type:
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        if credential_type not in ['zoho_client_id', 'zoho_client_secret']:
            return jsonify({'success': False, 'error': 'Invalid credential type'}), 400
        
        # Add debugging information
        current_app.logger.info(f'Credential verification attempt - User ID: {current_user.id}, Credential Type: {credential_type}, Password length: {len(password) if password else 0}')
        
        # Verify password using the User model's verify_password method
        password_verified = current_user.verify_password(password)
        current_app.logger.info(f'Credential password verification result: {password_verified}')
        
        if not password_verified:
            # Log failed attempt
            credential_logger.warning(f'Failed credential access attempt - User ID: {current_user.id}, IP: {request.remote_addr}, Credential Type: {credential_type}')
            return jsonify({'success': False, 'error': 'Invalid password'}), 401
        
        # Log successful verification
        credential_logger.info(f'Successful credential access verification - User ID: {current_user.id}, IP: {request.remote_addr}, Credential Type: {credential_type}')
        
        return jsonify({'success': True, 'message': 'Password verified successfully'})
        
    except Exception as e:
        credential_logger.error(f'Error in password verification - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@api_bp.route('/settings/get-zoho-credential', methods=['POST'])
@login_required
def get_zoho_credential():
    """Securely retrieve a specific Zoho credential"""
    try:
        data = request.get_json()
        credential_type = data.get('credential_type')
        
        if not credential_type:
            return jsonify({'success': False, 'error': 'Missing credential type'}), 400
        
        if credential_type not in ['zoho_client_id', 'zoho_client_secret']:
            return jsonify({'success': False, 'error': 'Invalid credential type'}), 400
        
        # Check if user has Zoho credentials (either encrypted or plain text)
        has_encrypted_credentials = current_user.zoho_client_id_hash and current_user.zoho_client_secret_hash
        has_plain_credentials = current_user.zoho_client_id and current_user.zoho_client_secret
        
        # Debug logging
        current_app.logger.info(f'Credential check - User ID: {current_user.id}, Has encrypted: {has_encrypted_credentials}, Has plain: {has_plain_credentials}, Client ID hash: {bool(current_user.zoho_client_id_hash)}, Client secret hash: {bool(current_user.zoho_client_secret_hash)}, Client ID plain: {bool(current_user.zoho_client_id)}, Client secret plain: {bool(current_user.zoho_client_secret)}')
        
        if not has_encrypted_credentials and not has_plain_credentials:
            credential_logger.warning(f'Credential access attempt for user without credentials - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({'success': False, 'error': 'No Zoho credentials found'}), 404
        
        # Get the requested credential
        if credential_type == 'zoho_client_id':
            encrypted_credential = current_user.zoho_client_id_hash
            credential_salt = current_user.zoho_client_id_salt
            # Check if we have the old plain text version as fallback
            plain_credential = current_user.zoho_client_id
        else:
            encrypted_credential = current_user.zoho_client_secret_hash
            credential_salt = current_user.zoho_client_secret_salt
            # Check if we have the old plain text version as fallback
            plain_credential = current_user.zoho_client_secret
        
        # Try to decrypt using the new Fernet system first
        credential = None
        if encrypted_credential and credential_salt:
            try:
                credential = verify_zoho_credential(encrypted_credential, credential_salt)
                current_app.logger.info(f'Successfully decrypted credential using Fernet - User ID: {current_user.id}, Credential Type: {credential_type}')
            except Exception as e:
                current_app.logger.warning(f'Failed to decrypt with Fernet - User ID: {current_user.id}, Credential Type: {credential_type}, Error: {str(e)}')
        
        # If Fernet decryption failed, try the old plain text as fallback
        if not credential and plain_credential:
            credential = plain_credential
            current_app.logger.info(f'Using plain text fallback - User ID: {current_user.id}, Credential Type: {credential_type}')
        
        if not credential:
            current_app.logger.error(f'Failed to retrieve credential - User ID: {current_user.id}, Credential Type: {credential_type}, Encrypted: {bool(encrypted_credential)}, Salt: {bool(credential_salt)}, Plain: {bool(plain_credential)}')
            return jsonify({'success': False, 'error': 'Failed to retrieve credential'}), 500
        
        # Log credential access
        credential_logger.info(f'Credential accessed - User ID: {current_user.id}, IP: {request.remote_addr}, Credential Type: {credential_type}, Timestamp: {datetime.utcnow()}')
        
        return jsonify({
            'success': True, 
            'credential': credential,
            'access_timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        current_app.logger.error(f'Error retrieving credential - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@api_bp.route('/settings/credential-access-logs', methods=['GET'])
@login_required
def get_credential_access_logs():
    """Get recent credential access logs for the current user"""
    try:
        # In a real implementation, you would store these logs in the database
        # For now, we'll return a summary of recent access
        log_file = 'logs/credential_access.log'
        
        if not os.path.exists(log_file):
            return jsonify({'success': True, 'logs': []})
        
        # Read recent logs (last 50 lines)
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_logs = lines[-50:] if len(lines) > 50 else lines
        
        # Filter logs for current user
        user_logs = []
        for log in recent_logs:
            if f'User ID: {current_user.id}' in log:
                user_logs.append(log.strip())
        
        return jsonify({
            'success': True,
            'logs': user_logs[-10:],  # Return last 10 user-specific logs
            'total_access_count': len(user_logs)
        })
        
    except Exception as e:
        credential_logger.error(f'Error retrieving access logs - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@api_bp.route('/verify-password', methods=['POST'])
@login_required
def verify_password():
    """General password verification endpoint"""
    try:
        data = request.get_json()
        password = data.get('password')
        
        if not password:
            return jsonify({'valid': False, 'error': 'Password is required'}), 400
        
        # Add debugging information
        current_app.logger.info(f'General password verification attempt - User ID: {current_user.id}, Password length: {len(password) if password else 0}')
        
        # Verify password using the User model's verify_password method
        password_verified = current_user.verify_password(password)
        current_app.logger.info(f'General password verification result: {password_verified}')
        
        if not password_verified:
            # Log failed attempt
            credential_logger.warning(f'Failed general password verification attempt - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({'valid': False, 'error': 'Invalid password'}), 401
        
        # Log successful verification
        credential_logger.info(f'Successful general password verification - User ID: {current_user.id}, IP: {request.remote_addr}')
        
        return jsonify({'valid': True, 'message': 'Password verified successfully'})
        
    except Exception as e:
        credential_logger.error(f'Error in general password verification - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'valid': False, 'error': 'Internal server error'}), 500

@api_bp.route('/settings/request-credential-access-code', methods=['POST'])
@login_required
def request_credential_access_code():
    """Request email verification code for credential access."""
    try:
        # Check rate limiting for email code requests
        rate_limit_check = check_rate_limit(current_user.id, 'email_code_requests')
        if not rate_limit_check['allowed']:
            credential_logger.warning(f'Rate limit exceeded for email code request - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({
                'success': False,
                'error': rate_limit_check['reason']
            }), 429  # Too Many Requests
        
        # Generate a 6-digit verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Store the code in user's session with expiration (5 minutes)
        current_user.credential_access_code = verification_code
        current_user.credential_access_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        db.session.commit()
        
        # Check if email is configured
        email_configured = all([
            current_app.config.get('MAIL_USERNAME'),
            current_app.config.get('MAIL_PASSWORD'),
            current_app.config.get('MAIL_DEFAULT_SENDER')
        ])
        
        if email_configured:
            # Send email with the code
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            email_sent = email_service.send_email(
                subject='Credential Access Verification Code',
                recipients=[current_user.email],
                template='verify_email',  # Using existing template
                user=current_user,
                verification_code=verification_code
            )
            
            if email_sent:
                credential_logger.info(f'Email verification code sent - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
                return jsonify({
                    'success': True,
                    'message': 'Verification code sent to your email',
                    'remaining_attempts': rate_limit_check['remaining_attempts']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send verification code via email'
                }), 500
        else:
            # Email not configured - return code in response for development/testing
            current_app.logger.warning(f"Email not configured. Returning code in response for user {current_user.id}")
            credential_logger.info(f'Verification code generated (email not configured) - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': True,
                'message': 'Email not configured. Use this verification code:',
                'verification_code': verification_code,  # Only for development/testing
                'email_configured': False,
                'remaining_attempts': rate_limit_check['remaining_attempts']
            })
            
    except Exception as e:
        current_app.logger.error(f"Error requesting credential access code: {str(e)}")
        return jsonify({'success': False, 'error': f'Error requesting verification code: {str(e)}'}), 500

@api_bp.route('/settings/verify-credential-access', methods=['POST'])
@login_required
def verify_credential_access():
    """Verify password and email code for credential access."""
    try:
        # Check rate limiting for verification attempts
        rate_limit_check = check_rate_limit(current_user.id, 'verification_attempts')
        if not rate_limit_check['allowed']:
            credential_logger.warning(f'Rate limit exceeded for verification attempt - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({
                'success': False,
                'error': rate_limit_check['reason']
            }), 429  # Too Many Requests
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        password = data.get('password')
        email_code = data.get('email_code')
        
        if not password or not email_code:
            return jsonify({'error': 'Both password and email code are required'}), 400
        
        # Verify password
        if not current_user.verify_password(password):
            credential_logger.warning(f'Failed credential verification - Invalid password - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'error': 'Invalid password',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Verify email code
        if (not current_user.credential_access_code or 
            not current_user.credential_access_code_expires_at or
            current_user.credential_access_code != email_code or
            datetime.utcnow() > current_user.credential_access_code_expires_at):
            credential_logger.warning(f'Failed credential verification - Invalid/expired email code - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'error': 'Invalid or expired email code',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Clear the used code
        current_user.credential_access_code = None
        current_user.credential_access_code_expires_at = None
        db.session.commit()
        
        # Set up credential access session (15 minutes)
        current_user.credential_access_verified = True
        current_user.credential_access_expires_at = datetime.utcnow() + timedelta(minutes=15)
        db.session.commit()
        
        credential_logger.info(f'Successful credential verification - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
        
        return jsonify({
            'success': True,
            'message': 'Credential access verified successfully',
            'expires_at': current_user.credential_access_expires_at.isoformat(),
            'remaining_attempts': rate_limit_check['remaining_attempts']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error verifying credential access: {str(e)}")
        return jsonify({'error': f'Error verifying credential access: {str(e)}'}), 500

@api_bp.route('/settings/verify-enhanced-disconnect', methods=['POST'])
@login_required
def verify_enhanced_disconnect():
    """Enhanced verification for Zoho disconnect - requires password, email code, client ID, and client secret."""
    try:
        # Check rate limiting for verification attempts
        rate_limit_check = check_rate_limit(current_user.id, 'enhanced_disconnect_verification')
        if not rate_limit_check['allowed']:
            credential_logger.warning(f'Rate limit exceeded for enhanced disconnect verification - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({
                'success': False,
                'error': rate_limit_check['reason']
            }), 429  # Too Many Requests
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        password = data.get('password')
        email_code = data.get('email_code')
        client_id = data.get('client_id')
        client_secret = data.get('client_secret')
        
        if not password or not email_code or not client_id or not client_secret:
            return jsonify({'success': False, 'error': 'All fields are required: password, email_code, client_id, client_secret'}), 400
        
        # Verify password
        if not current_user.verify_password(password):
            credential_logger.warning(f'Failed enhanced disconnect verification - Invalid password - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': False,
                'error': 'Invalid password',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Verify email code
        if (not current_user.enhanced_disconnect_code or 
            not current_user.enhanced_disconnect_code_expires_at or
            current_user.enhanced_disconnect_code != email_code or
            datetime.utcnow() > current_user.enhanced_disconnect_code_expires_at):
            credential_logger.warning(f'Failed enhanced disconnect verification - Invalid/expired email code - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': False,
                'error': 'Invalid or expired email code',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Verify client ID
        stored_client_id = None
        if current_user.zoho_client_id_hash and current_user.zoho_client_id_salt:
            try:
                stored_client_id = verify_zoho_credential(current_user.zoho_client_id_hash, current_user.zoho_client_id_salt)
            except Exception as e:
                current_app.logger.warning(f'Failed to decrypt client ID for verification - User ID: {current_user.id}, Error: {str(e)}')
        
        # Fallback to plain text if encrypted version failed
        if not stored_client_id and current_user.zoho_client_id:
            stored_client_id = current_user.zoho_client_id
        
        if not stored_client_id or not secrets.compare_digest(stored_client_id, client_id):
            credential_logger.warning(f'Failed enhanced disconnect verification - Invalid client ID - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': False,
                'error': 'Invalid client ID',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Verify client secret
        stored_client_secret = None
        if current_user.zoho_client_secret_hash and current_user.zoho_client_secret_salt:
            try:
                stored_client_secret = verify_zoho_credential(current_user.zoho_client_secret_hash, current_user.zoho_client_secret_salt)
            except Exception as e:
                current_app.logger.warning(f'Failed to decrypt client secret for verification - User ID: {current_user.id}, Error: {str(e)}')
        
        # Fallback to plain text if encrypted version failed
        if not stored_client_secret and current_user.zoho_client_secret:
            stored_client_secret = current_user.zoho_client_secret
        
        if not stored_client_secret or not secrets.compare_digest(stored_client_secret, client_secret):
            credential_logger.warning(f'Failed enhanced disconnect verification - Invalid client secret - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': False,
                'error': 'Invalid client secret',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Clear the used email code
        current_user.enhanced_disconnect_code = None
        current_user.enhanced_disconnect_code_expires_at = None
        db.session.commit()
        
        credential_logger.info(f'Successful enhanced disconnect verification - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
        
        return jsonify({
            'success': True,
            'message': 'Enhanced verification successful',
            'remaining_attempts': rate_limit_check['remaining_attempts']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in enhanced disconnect verification: {str(e)}")
        return jsonify({'success': False, 'error': f'Error in enhanced verification: {str(e)}'}), 500

@api_bp.route('/settings/request-enhanced-disconnect-code', methods=['POST'])
@login_required
def request_enhanced_disconnect_code():
    """Request email verification code specifically for enhanced disconnect verification."""
    try:
        # Check rate limiting for enhanced disconnect email code requests
        rate_limit_check = check_rate_limit(current_user.id, 'enhanced_disconnect_email_requests')
        if not rate_limit_check['allowed']:
            credential_logger.warning(f'Rate limit exceeded for enhanced disconnect email code request - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({
                'success': False,
                'error': rate_limit_check['reason']
            }), 429  # Too Many Requests
        
        # Generate a 6-digit verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Store the code in user's session with expiration (5 minutes)
        current_user.enhanced_disconnect_code = verification_code
        current_user.enhanced_disconnect_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        db.session.commit()
        
        # Check if email is configured
        email_configured = all([
            current_app.config.get('MAIL_USERNAME'),
            current_app.config.get('MAIL_PASSWORD'),
            current_app.config.get('MAIL_DEFAULT_SENDER')
        ])
        
        if email_configured:
            # Send email with the code
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            email_sent = email_service.send_email(
                subject='Enhanced Disconnect Verification Code',
                recipients=[current_user.email],
                template='verify_email',  # Using existing template
                user=current_user,
                verification_code=verification_code
            )
            
            if email_sent:
                credential_logger.info(f'Enhanced disconnect email verification code sent - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
                return jsonify({
                    'success': True,
                    'message': 'Enhanced disconnect verification code sent to your email',
                    'remaining_attempts': rate_limit_check['remaining_attempts']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send enhanced disconnect verification code via email'
                }), 500
        else:
            # Email not configured - return code in response for development/testing
            current_app.logger.warning(f"Email not configured. Returning enhanced disconnect code in response for user {current_user.id}")
            credential_logger.info(f'Enhanced disconnect verification code generated (email not configured) - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': True,
                'message': 'Email not configured. Use this enhanced disconnect verification code:',
                'verification_code': verification_code,  # Only for development/testing
                'email_configured': False,
                'remaining_attempts': rate_limit_check['remaining_attempts']
            })
            
    except Exception as e:
        current_app.logger.error(f"Error requesting enhanced disconnect code: {str(e)}")
        return jsonify({'success': False, 'error': f'Error requesting enhanced disconnect verification code: {str(e)}'}), 500

@api_bp.route('/settings/request-report-deletion-code', methods=['POST'])
@login_required
def request_report_deletion_code():
    """Request email verification code specifically for report deletion verification."""
    try:
        # Check rate limiting for report deletion email code requests
        rate_limit_check = check_rate_limit(current_user.id, 'report_deletion_email_requests')
        if not rate_limit_check['allowed']:
            credential_logger.warning(f'Rate limit exceeded for report deletion email code request - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({
                'success': False,
                'error': rate_limit_check['reason']
            }), 429  # Too Many Requests
        
        # Generate a 6-digit verification code
        verification_code = ''.join(random.choices(string.digits, k=6))
        
        # Store the code in user's session with expiration (5 minutes)
        current_user.report_deletion_code = verification_code
        current_user.report_deletion_code_expires_at = datetime.utcnow() + timedelta(minutes=5)
        
        db.session.commit()
        
        # Check if email is configured
        email_configured = all([
            current_app.config.get('MAIL_USERNAME'),
            current_app.config.get('MAIL_PASSWORD'),
            current_app.config.get('MAIL_DEFAULT_SENDER')
        ])
        
        if email_configured:
            # Send email with the code
            from app.services.email_service import EmailService
            email_service = EmailService()
            
            email_sent = email_service.send_email(
                subject='Report Deletion Verification Code',
                recipients=[current_user.email],
                template='verify_email',  # Using existing template
                user=current_user,
                verification_code=verification_code
            )
            
            if email_sent:
                credential_logger.info(f'Report deletion email verification code sent - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
                return jsonify({
                    'success': True,
                    'message': 'Report deletion verification code sent to your email',
                    'remaining_attempts': rate_limit_check['remaining_attempts']
                })
            else:
                return jsonify({
                    'success': False,
                    'error': 'Failed to send report deletion verification code via email'
                }), 500
        else:
            # Email not configured - return code in response for development/testing
            current_app.logger.warning(f"Email not configured. Returning report deletion code in response for user {current_user.id}")
            credential_logger.info(f'Report deletion verification code generated (email not configured) - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': True,
                'message': 'Email not configured. Use this report deletion verification code:',
                'verification_code': verification_code,  # Only for development/testing
                'email_configured': False,
                'remaining_attempts': rate_limit_check['remaining_attempts']
            })
            
    except Exception as e:
        current_app.logger.error(f"Error requesting report deletion code: {str(e)}")
        return jsonify({'success': False, 'error': f'Error requesting report deletion verification code: {str(e)}'}), 500

@api_bp.route('/settings/verify-report-deletion', methods=['POST'])
@login_required
def verify_report_deletion():
    """Enhanced verification for report deletion - requires password and email code."""
    try:
        # Check rate limiting for verification attempts
        rate_limit_check = check_rate_limit(current_user.id, 'report_deletion_verification')
        if not rate_limit_check['allowed']:
            credential_logger.warning(f'Rate limit exceeded for report deletion verification - User ID: {current_user.id}, IP: {request.remote_addr}')
            return jsonify({
                'success': False,
                'error': rate_limit_check['reason']
            }), 429  # Too Many Requests
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        password = data.get('password')
        email_code = data.get('email_code')
        
        if not password or not email_code:
            return jsonify({'success': False, 'error': 'Both password and email code are required'}), 400
        
        # Verify password
        if not current_user.verify_password(password):
            credential_logger.warning(f'Failed report deletion verification - Invalid password - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': False,
                'error': 'Invalid password',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Verify email code
        if (not current_user.report_deletion_code or 
            not current_user.report_deletion_code_expires_at or
            current_user.report_deletion_code != email_code or
            datetime.utcnow() > current_user.report_deletion_code_expires_at):
            credential_logger.warning(f'Failed report deletion verification - Invalid/expired email code - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
            return jsonify({
                'success': False,
                'error': 'Invalid or expired email code',
                'remaining_attempts': rate_limit_check['remaining_attempts']
            }), 401
        
        # Clear the used email code
        current_user.report_deletion_code = None
        current_user.report_deletion_code_expires_at = None
        db.session.commit()
        
        credential_logger.info(f'Successful report deletion verification - User ID: {current_user.id}, IP: {request.remote_addr}, Remaining attempts: {rate_limit_check["remaining_attempts"]}')
        
        return jsonify({
            'success': True,
            'message': 'Report deletion verification successful',
            'remaining_attempts': rate_limit_check['remaining_attempts']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error in report deletion verification: {str(e)}")
        return jsonify({'success': False, 'error': f'Error in report deletion verification: {str(e)}'}), 500

@api_bp.route('/settings/debug-credentials', methods=['GET'])
@login_required
def debug_credentials():
    """Debug endpoint to check what credentials the user has stored."""
    try:
        user = current_user
        
        credential_info = {
            'user_id': user.id,
            'has_client_id_plain': bool(user.zoho_client_id),
            'has_client_secret_plain': bool(user.zoho_client_secret),
            'has_client_id_hash': bool(user.zoho_client_id_hash),
            'has_client_secret_hash': bool(user.zoho_client_secret_hash),
            'has_client_id_salt': bool(user.zoho_client_id_salt),
            'has_client_secret_salt': bool(user.zoho_client_secret_salt),
            'client_id_length': len(user.zoho_client_id) if user.zoho_client_id else 0,
            'client_secret_length': len(user.zoho_client_secret) if user.zoho_client_secret else 0,
            'client_id_hash_length': len(user.zoho_client_id_hash) if user.zoho_client_id_hash else 0,
            'client_secret_hash_length': len(user.zoho_client_secret_hash) if user.zoho_client_secret_hash else 0,
        }
        
        current_app.logger.info(f'Debug credentials - User ID: {user.id}, Info: {credential_info}')
        
        return jsonify({
            'success': True,
            'credential_info': credential_info
        })
        
    except Exception as e:
        current_app.logger.error(f'Error in debug credentials - User ID: {current_user.id}, Error: {str(e)}')
        return jsonify({'success': False, 'error': 'Internal server error'}), 500 