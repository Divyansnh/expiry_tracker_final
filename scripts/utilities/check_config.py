import os
from app import create_app
from app.config import Config

app = create_app()

print("\nEnvironment Variables:")
print("ZOHO_CLIENT_ID:", os.environ.get('ZOHO_CLIENT_ID'))
print("ZOHO_CLIENT_SECRET:", os.environ.get('ZOHO_CLIENT_SECRET'))
print("ZOHO_REDIRECT_URI:", os.environ.get('ZOHO_REDIRECT_URI'))
print("ZOHO_ORGANIZATION_ID:", os.environ.get('ZOHO_ORGANIZATION_ID'))

print("\nApp Configuration:")
print("ZOHO_CLIENT_ID:", app.config.get('ZOHO_CLIENT_ID'))
print("ZOHO_CLIENT_SECRET:", app.config.get('ZOHO_CLIENT_SECRET'))
print("ZOHO_REDIRECT_URI:", app.config.get('ZOHO_REDIRECT_URI'))
print("ZOHO_ORGANIZATION_ID:", app.config.get('ZOHO_ORGANIZATION_ID')) 