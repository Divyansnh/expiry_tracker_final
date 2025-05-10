from functools import wraps
from flask import request, g, current_app, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models.user import User
import time

def log_request(app):
    """Log all requests to the application."""
    start_times = {}
    
    @app.before_request
    def before_request():
        start_times[request.environ['werkzeug.request']] = time.time()
    
    @app.after_request
    def after_request(response):
        # Don't log sensitive information in URLs
        path = request.path
        if '/auth/zoho/callback' in path:
            path = '/auth/zoho/callback'  # Hide the callback parameters
        elif '/auth' in path:
            path = '/auth/***'  # Hide auth-related paths
        
        duration = time.time() - start_times.get(request.environ['werkzeug.request'], time.time())
        app.logger.info(
            'Request: %s %s - Status: %s - Duration: %.2fs',
            request.method,
            path,
            response.status_code,
            duration
        )
        return response

def require_auth(f):
    """Require authentication for routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        g.user = User.query.get(user_id)
        return f(*args, **kwargs)
    return decorated

def require_admin(f):
    """Require admin privileges for routes."""
    @wraps(f)
    def decorated(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin privileges required'}), 403
        
        g.user = user
        return f(*args, **kwargs)
    return decorated

def handle_cors(app):
    """Handle CORS headers."""
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin:
            # Only allow specific origins in production
            if app.debug:
                response.headers.add('Access-Control-Allow-Origin', origin)
            else:
                allowed_origins = app.config.get('ALLOWED_ORIGINS', [])
                if origin in allowed_origins:
                    response.headers.add('Access-Control-Allow-Origin', origin)
            
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-CSRFToken')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            response.headers.add('Access-Control-Expose-Headers', 'Set-Cookie')
            response.headers.add('Access-Control-Allow-Credentials', 'true')
            response.headers.add('Vary', 'Origin')
        return response

def rate_limit():
    """Rate limiting middleware."""
    # TODO: Implement rate limiting
    pass

def validate_request(app):
    """Validate request data."""
    @app.before_request
    def before_request():
        if request.is_json:
            try:
                request.get_json()
            except Exception as e:
                app.logger.error(f'Invalid JSON in request: {str(e)}')
                return jsonify({'error': 'Invalid JSON'}), 400 