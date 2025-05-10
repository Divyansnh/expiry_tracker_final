"""API v1 package."""

from flask import Blueprint
from app.api.v1.date_ocr import date_ocr_bp

api_bp = Blueprint('api', __name__)

# Register date_ocr blueprint under api_bp
api_bp.register_blueprint(date_ocr_bp, url_prefix='/date_ocr')

from app.api.v1 import auth, inventory, notifications, items 