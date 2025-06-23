"""API v1 package."""

from app.api.v1.blueprint import api_bp

# Import modules after creating the Blueprint to avoid circular imports
from app.api.v1 import notifications, items, date_ocr, reports, settings 