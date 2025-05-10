from flask import current_app, render_template
from flask_mail import Message
from app.core.extensions import mail
from app.models.user import User
from typing import List, Dict, Any, Optional, Union, Literal
import logging
import smtplib

logger = logging.getLogger(__name__)

EmailTemplate = Literal[
    'verify_email',
    'reset_password',
    'daily_notification',
    'password_reset_confirmation'
]

class EmailService:
    """Service for handling email communications."""
    
    def __init__(self) -> None:
        self.mail = mail
    
    def send_email(
        self,
        subject: str,
        recipients: List[str],
        template: EmailTemplate,
        **kwargs: Any
    ) -> bool:
        """Send an email using a template.
        
        Args:
            subject: Email subject
            recipients: List of recipient email addresses
            template: Name of the template to use
            **kwargs: Additional arguments to pass to the template
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            logger.info(f"Preparing to send email to {recipients}")
            logger.info(f"Using template: {template}")
            logger.info(f"Template kwargs: {kwargs}")
            
            # Verify email configuration
            if not all([
                current_app.config['MAIL_SERVER'],
                current_app.config['MAIL_PORT'],
                current_app.config['MAIL_USERNAME'],
                current_app.config['MAIL_PASSWORD'],
                current_app.config['MAIL_DEFAULT_SENDER']
            ]):
                logger.error("Incomplete email configuration")
                logger.error(f"Mail server: {current_app.config['MAIL_SERVER']}")
                logger.error(f"Mail port: {current_app.config['MAIL_PORT']}")
                logger.error(f"Mail username: {current_app.config['MAIL_USERNAME']}")
                logger.error(f"Mail default sender: {current_app.config['MAIL_DEFAULT_SENDER']}")
                return False
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            # Log email configuration
            logger.info(f"Mail server: {current_app.config['MAIL_SERVER']}")
            logger.info(f"Mail port: {current_app.config['MAIL_PORT']}")
            logger.info(f"Mail use TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Mail username: {current_app.config['MAIL_USERNAME']}")
            
            try:
                template_path = f'emails/{template}.html'
                logger.info(f"Attempting to render template: {template_path}")
                msg.html = render_template(template_path, **kwargs)
                logger.info("Email template rendered successfully")
            except Exception as template_error:
                logger.error(f"Error rendering email template {template_path}: {str(template_error)}", exc_info=True)
                return False
            
            try:
                self.mail.send(msg)
                logger.info(f"Email sent successfully to {recipients}")
                return True
            except smtplib.SMTPAuthenticationError as auth_error:
                logger.error("SMTP Authentication failed. Check username and password.")
                logger.error(f"Error details: {str(auth_error)}")
                return False
            except smtplib.SMTPException as smtp_error:
                logger.error(f"SMTP error while sending email: {str(smtp_error)}")
                logger.error(f"Error type: {smtp_error.__class__.__name__}")
                return False
            except Exception as send_error:
                logger.error(f"Unexpected error sending email: {str(send_error)}")
                logger.error(f"Error type: {send_error.__class__.__name__}")
                return False
                
        except Exception as e:
            logger.error(f"Error in send_email: {str(e)}", exc_info=True)
            logger.error(f"Full error details: {e.__class__.__name__}: {str(e)}")
            return False
    
    def send_verification_email(self, user: User) -> bool:
        """Send verification email to user.
        
        Args:
            user: User to send verification email to
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Check if user has a valid email
            if not user.email:
                logger.error("User email is None")
                return False
                
            # Generate verification code
            user.generate_verification_code()
            
            # Log the attempt with configuration details
            logger.info(f"Attempting to send verification email to {user.email}")
            logger.info(f"Mail server config: {current_app.config['MAIL_SERVER']}:{current_app.config['MAIL_PORT']}")
            logger.info(f"Using TLS: {current_app.config['MAIL_USE_TLS']}")
            logger.info(f"Sender: {current_app.config['MAIL_DEFAULT_SENDER']}")
            
            # Ensure email is a string
            user_email: str = str(user.email)
            
            return self.send_email(
                subject="Verify Your Email",
                recipients=[user_email],
                template='verify_email',
                user=user,
                verification_code=user.verification_code
            )
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error while sending verification email: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return False
    
    def send_password_reset_email(self, email: str, token: str) -> bool:
        """Send password reset email.
        
        Args:
            email: Email address to send reset link to
            token: Password reset token
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        logger.info(f"Attempting to send password reset email to {email}")
        logger.info(f"Reset URL: {token}")
        result = self.send_email(
            subject='Reset Your Password - Expiry Tracker',
            recipients=[email],
            template='reset_password',
            email=email,
            reset_url=token
        )
        logger.info(f"Password reset email send result: {result}")
        return result
    
    def send_daily_notification_email(self, user: User, items: List[Dict[str, Any]]) -> bool:
        """Send daily notification email with items that need attention.
        
        Args:
            user: User to send notification to
            items: List of items to notify about
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        if not items:
            logger.info("No items to notify about")
            return False
            
        # Filter out test items and set priority
        items_needing_attention = []
        for item in items:
            if not item['name'].lower().startswith('test'):
                # Set priority based on days until expiry
                if item['days_until_expiry'] <= 1:  # Today or tomorrow
                    priority = 'high'
                elif item['days_until_expiry'] <= 7:  # Within 7 days
                    priority = 'normal'
                else:  # More than 7 days
                    priority = 'low'
                
                items_needing_attention.append({
                    **item,
                    'priority': priority
                })
        
        if not items_needing_attention:
            logger.info("No items need attention at this time")
            return False
            
        # Sort items by days until expiry
        items_needing_attention.sort(key=lambda x: x['days_until_expiry'])
        
        # Prepare email content
        subject = "Expiry Tracker - Daily Item Status Update"
        template = 'daily_notification'
        
        # Ensure email is a string and not None
        if not user.email:
            logger.error("User email is None")
            return False
        user_email: str = str(user.email)
        
        # Send email
        result = self.send_email(
            subject=subject,
            recipients=[user_email],
            template=template,
            user=user,
            items=items_needing_attention
        )
        
        if result:
            logger.info(f"Sent daily notification email to {user_email} with {len(items_needing_attention)} items")
        
        return result
    
    def send_password_reset_confirmation(self, user: Union[User, str]) -> bool:
        """Send password reset confirmation email.
        
        Args:
            user: Either a User object or an email string to send confirmation to
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        # Handle both User object and email string
        if isinstance(user, User):
            if not user.email:
                logger.error("User email is None")
                return False
            user_email = str(user.email)
            template_user = user
        else:
            user_email = str(user)
            template_user = None
        
        logger.info(f"Sending password reset confirmation to {user_email}")
        return self.send_email(
            subject='Password Reset Confirmation',
            recipients=[user_email],
            template='password_reset_confirmation',
            user=template_user,
            email=user_email  # Pass email separately for template
        ) 