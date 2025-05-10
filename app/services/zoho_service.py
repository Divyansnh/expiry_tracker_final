import os
import time
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Literal
from flask import current_app, session, request
from flask_login import current_user
from app.core.extensions import db
from app.models.item import Item, STATUS_EXPIRED, STATUS_ACTIVE, STATUS_EXPIRING_SOON, STATUS_PENDING
from app.models.user import User
from urllib.parse import urlencode

class ZohoService:
    """Service for interacting with Zoho Inventory API."""
    
    def __init__(self, user: User) -> None:
        """Initialize service with user."""
        self.user: User = user
        self.client_id: str = user.zoho_client_id or current_app.config['ZOHO_CLIENT_ID']
        self.client_secret: str = user.zoho_client_secret or current_app.config['ZOHO_CLIENT_SECRET']
        self.redirect_uri: str = current_app.config['ZOHO_REDIRECT_URI']
        self.base_url: str = current_app.config['ZOHO_API_BASE_URL']
        self.accounts_url: str = current_app.config['ZOHO_ACCOUNTS_URL']
        
        # Don't log sensitive information
        current_app.logger.info("Zoho service initialized for user: %s", user.username)
    
    def get_access_token(self) -> Optional[str]:
        """Get the current access token from user record."""
        if not self.user:
            current_app.logger.error("No user available")
            return None
            
        # Check if token exists and is not expired
        if self.user.zoho_access_token and self.user.zoho_token_expires_at:
            if datetime.now() >= self.user.zoho_token_expires_at:
                current_app.logger.info("Access token expired, attempting to refresh")
                if self.refresh_token():
                    return self.user.zoho_access_token
                return None
            return self.user.zoho_access_token
            
        current_app.logger.error("No access token available")
        return None
    
    def get_refresh_token(self) -> Optional[str]:
        """Get the refresh token from user record."""
        return self.user.zoho_refresh_token if self.user else None
    
    def refresh_token(self) -> bool:
        """Refresh the access token using the refresh token."""
        refresh_token = self.get_refresh_token()
        if not refresh_token:
            current_app.logger.error("No refresh token available")
            return False
        
        try:
            response = requests.post(
                f"{self.accounts_url}/oauth/v2/token",
                data={
                    'refresh_token': refresh_token,
                    'client_id': self.client_id,
                    'client_secret': self.client_secret,
                    'grant_type': 'refresh_token'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'access_token' not in data:
                    current_app.logger.error(f"Invalid refresh token response: {data}")
                    return False
                    
                self.user.zoho_access_token = data['access_token']
                self.user.zoho_token_expires_at = datetime.now() + timedelta(seconds=data.get('expires_in', 3600))
                db.session.commit()
                current_app.logger.info("Successfully refreshed access token")
                return True
                
            current_app.logger.error(f"Failed to refresh token: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error refreshing Zoho token: {str(e)}")
            return False
    
    def get_inventory(self) -> Optional[List[Dict[str, Any]]]:
        """Get inventory data from Zoho."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
            
        try:
            current_app.logger.info("Fetching inventory data from Zoho")
            
            # Get items
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'status': 'active'
                }
            )
            
            if response.status_code == 401:
                current_app.logger.error("Unauthorized - token may be invalid")
                return None
                
            if response.status_code != 200:
                current_app.logger.error(f"Failed to get inventory: {response.status_code} - {response.text}")
                return None
                
            try:
                data = response.json()
                if not isinstance(data, dict) or 'items' not in data:
                    current_app.logger.error(f"Invalid response format: {data}")
                    return None
                    
                current_app.logger.info(f"Successfully fetched {len(data['items'])} items from Zoho")
                return data['items']
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse inventory response: {response.text}")
                return None
            
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Error making API request: {str(e)}")
            return None
        except Exception as e:
            current_app.logger.error(f"Unexpected error: {str(e)}")
            return None
    
    def sync_inventory(self, user: User) -> Dict[str, Union[int, bool]]:
        """Sync inventory with Zoho."""
        try:
            current_app.logger.info("Fetching inventory data from Zoho")
            
            # Get access token
            access_token = self.get_access_token()
            if not access_token:
                current_app.logger.error("No access token available")
                return {"success": False, "synced": 0}
            
            # Fetch inventory data from Zoho
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'status': 'active'
                }
            )
            
            if response.status_code == 401:
                current_app.logger.error("Unauthorized - token may be invalid")
                return {"success": False, "synced": 0}
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to fetch inventory: {response.status_code} - {response.text}")
                return {"success": False, "synced": 0}
            
            try:
                data = response.json()
                if not isinstance(data, dict) or 'items' not in data:
                    current_app.logger.error(f"Invalid response format: {data}")
                    return {"success": False, "synced": 0}
                    
                items = data['items']
                current_app.logger.info(f"Successfully fetched {len(items)} active items from Zoho")
                
                # Get all local items for this user
                local_items = {item.name.lower(): item for item in Item.query.filter_by(user_id=user.id).all()}
                
                synced_count = 0
                for zoho_item in items:
                    item_name = zoho_item['name']
                    current_app.logger.info(f"Processing item: {item_name}")
                    
                    # Check if item exists locally
                    local_item = local_items.get(item_name.lower())
                    
                    if local_item:
                        # Only update Zoho-specific fields, preserve local changes
                        current_app.logger.info(f"Updating existing item: {item_name} (Zoho ID: {zoho_item['item_id']})")
                        local_item.zoho_item_id = zoho_item['item_id']
                        
                        # Never overwrite these fields from Zoho
                        protected_fields = [
                            'quantity',
                            'unit',
                            'cost_price',
                            'selling_price',
                            'status',
                            'location',
                            'notes',
                            'purchase_price',
                            'expiry_date'
                        ]
                        
                        # Only update non-protected fields
                        if not local_item.updated_at or (datetime.now() - local_item.updated_at).total_seconds() > 300:  # 5 minutes
                            local_item.name = zoho_item['name']
                            local_item.description = zoho_item.get('description', '')
                        
                        db.session.add(local_item)
                    else:
                        # Create new item
                        current_app.logger.info(f"Creating new item: {item_name}")
                        item = Item(
                            name=zoho_item['name'],
                            description=zoho_item.get('description', ''),
                            quantity=float(zoho_item.get('stock_on_hand', 0)),
                            unit=zoho_item.get('unit', ''),
                            selling_price=float(zoho_item.get('rate', 0)),
                            cost_price=float(zoho_item.get('purchase_rate', 0)),
                            expiry_date=datetime.strptime(zoho_item['expiry_date'], '%Y-%m-%d').date() if zoho_item.get('expiry_date') else None,
                            status=STATUS_ACTIVE,  # New items start as active
                            zoho_item_id=zoho_item['item_id'],
                            user_id=user.id
                        )
                        db.session.add(item)
                    
                    synced_count += 1
                
                db.session.commit()
                current_app.logger.info("Successfully synced inventory with Zoho")
                return {"success": True, "synced": synced_count}
                
            except json.JSONDecodeError as e:
                current_app.logger.error(f"Failed to parse inventory response: {response.text}")
                return {"success": False, "synced": 0}
            
        except Exception as e:
            current_app.logger.error(f"Error syncing inventory: {str(e)}")
            db.session.rollback()
            return {"success": False, "synced": 0}
    
    def get_auth_url(self) -> str:
        """Get the Zoho OAuth authorization URL."""
        params = {
            'response_type': 'code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'scope': 'ZohoInventory.FullAccess.all',
            'access_type': 'offline',
            'prompt': 'consent'
        }
        
        # Don't log sensitive parameters
        current_app.logger.info("Generating Zoho auth URL")
        auth_url = f"{self.accounts_url}/oauth/v2/auth"
        query_string = urlencode(params)
        full_url = f"{auth_url}?{query_string}"
        current_app.logger.info("Generated Zoho auth URL")
        return full_url
    
    def handle_callback(self, code: str) -> bool:
        """Handle the OAuth callback and store tokens."""
        try:
            # Exchange code for tokens
            token_url = f"{self.accounts_url}/oauth/v2/token"
            current_app.logger.info("Processing Zoho OAuth callback")
            
            data = {
                'code': code,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'redirect_uri': self.redirect_uri,
                'grant_type': 'authorization_code',
                'access_type': 'offline'
            }
            
            response = requests.post(token_url, data=data)
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to get Zoho token: {response.status_code}")
                return False
                
            try:
                token_data = response.json()
                # Don't log token data
                current_app.logger.info("Successfully received Zoho token response")
            except json.JSONDecodeError as e:
                current_app.logger.error("Failed to parse Zoho token response")
                return False
            
            # Check if we got all required tokens
            if 'access_token' not in token_data or 'refresh_token' not in token_data:
                current_app.logger.error("Missing required tokens in Zoho response")
                return False
                
            # Store tokens in user's database record
            self.user.zoho_access_token = token_data['access_token']
            self.user.zoho_refresh_token = token_data['refresh_token']
            self.user.zoho_token_expires_at = datetime.now() + timedelta(seconds=token_data.get('expires_in', 3600))
            
            # Commit token changes first
            db.session.commit()
            current_app.logger.info(f"Successfully stored Zoho tokens for user {self.user.id}")
            
            # Try to get organization ID, but don't fail if we can't
            try:
                org_response = requests.get(
                    f"{self.base_url}/organizations",
                    headers={
                        'Authorization': f'Bearer {token_data["access_token"]}',
                        'Content-Type': 'application/json'
                    }
                )
                
                if org_response.status_code == 200:
                    try:
                        org_data = org_response.json()
                        # Don't log sensitive organization data
                        current_app.logger.info(f"Successfully retrieved Zoho organization data for user {self.user.id}")
                        if org_data.get('organizations'):
                            self.user.zoho_organization_id = org_data['organizations'][0]['organization_id']
                            db.session.commit()
                            current_app.logger.info(f"Successfully stored Zoho organization ID for user {self.user.id}")
                    except json.JSONDecodeError as e:
                        current_app.logger.error("Failed to parse Zoho organization response")
                else:
                    current_app.logger.error(f"Failed to get Zoho organization ID: {org_response.status_code}")
            except Exception as e:
                current_app.logger.error(f"Error getting Zoho organization ID: {str(e)}")
                # Don't fail the whole process if we can't get the organization ID
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error handling Zoho callback: {str(e)}")
            db.session.rollback()
            return False

    def get_item_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get an item from Zoho by name."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
            
        try:
            # First try to find active items
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'name': name,
                    'status': 'active'  # Check active items first
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    current_app.logger.info(f"Found active item with name '{name}' in Zoho")
                    return items[0]
            
            # If no active items found, check inactive items
            response = requests.get(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                params={
                    'name': name,
                    'status': 'inactive'  # Check inactive items
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get('items', [])
                if items:
                    current_app.logger.info(f"Found inactive item with name '{name}' in Zoho")
                    return items[0]
            
            current_app.logger.info(f"No items found with name '{name}' in Zoho")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting item from Zoho: {str(e)}")
            return None

    def create_item_in_zoho(self, item_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new item in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
        
        try:
            current_app.logger.info(f"Creating item in Zoho: {item_data['name']}")
            
            # Check if item already exists
            existing_item = self.get_item_by_name(item_data['name'])
            if existing_item:
                # Check if item exists in local database
                local_item = Item.query.filter_by(zoho_item_id=existing_item['item_id']).first()
                if local_item:
                    # Update existing local item
                    local_item.name = item_data['name']
                    local_item.description = item_data.get('description', '')
                    local_item.quantity = float(item_data.get('quantity', 0))
                    local_item.unit = item_data['unit']
                    local_item.selling_price = float(item_data['selling_price'])
                    local_item.cost_price = float(item_data.get('cost_price', 0))
                    local_item.expiry_date = datetime.strptime(item_data['expiry_date'], '%Y-%m-%d').date()
                    local_item.status = item_data.get('status', 'active')
                    db.session.commit()
                    current_app.logger.info(f"Updated existing local item: {local_item.name}")
                    return existing_item
                
                if existing_item.get('status') == 'inactive':
                    current_app.logger.info(f"Found inactive item '{item_data['name']}' in Zoho. Reactivating it.")
                    # Reactivate the item and update all details including stock
                    response = requests.put(
                        f"{self.base_url}/items/{existing_item['item_id']}",
                        headers={
                            'Authorization': f'Bearer {access_token}',
                            'Content-Type': 'application/json'
                        },
                        json={
                            "status": "active",
                            "name": item_data['name'],
                            "unit": item_data['unit'],
                            "rate": float(item_data['selling_price']),
                            "purchase_rate": float(item_data.get('cost_price', 0)),
                            "description": item_data.get('description', ''),
                            "initial_stock": float(item_data['quantity']),
                            "initial_stock_rate": float(item_data.get('cost_price', 0))
                        }
                    )
                    
                    if response.status_code == 200:
                        current_app.logger.info(f"Successfully reactivated item in Zoho: {existing_item['item_id']}")
                        return existing_item
                    else:
                        current_app.logger.error(f"Failed to reactivate item in Zoho: {response.status_code} - {response.text}")
                else:
                    current_app.logger.info(f"Item '{item_data['name']}' already exists in Zoho. Linking to existing item.")
                    return existing_item
            
            # Determine status based on expiry date
            expiry_date = datetime.strptime(item_data['expiry_date'], '%Y-%m-%d').date()
            current_date = datetime.now().date()
            status = "inactive" if expiry_date <= current_date else "active"
            
            # Create item with basic details and initial stock
            request_data = {
                "name": item_data['name'],
                "unit": item_data['unit'],
                "rate": float(item_data['selling_price']),
                "purchase_rate": float(item_data.get('cost_price', 0)),
                "description": item_data.get('description', ''),
                "status": status,
                "item_type": "inventory",
                "product_type": "goods",
                "initial_stock": float(item_data['quantity']),
                "initial_stock_rate": float(item_data.get('cost_price', 0))
            }
            
            current_app.logger.info(f"Creating item in Zoho with data: {request_data}")
            
            response = requests.post(
                f"{self.base_url}/items",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=request_data
            )
            
            if response.status_code == 201:
                data = response.json()
                item = data.get('item')
                current_app.logger.info(f"Successfully created item in Zoho: {data}")
                return item
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.create_item_in_zoho(item_data)
            
            current_app.logger.error(f"Failed to create item in Zoho: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error creating item in Zoho: {str(e)}")
            return None

    def update_item_in_zoho(self, item_id: str, item_data: Dict[str, Any]) -> Optional[Dict]:
        """Update an existing item in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
        
        try:
            current_app.logger.info(f"Updating item in Zoho: {item_id}")
            
            # First update the item details
            update_data = {
                "name": item_data['name'],
                "unit": item_data['unit'],
                "rate": float(item_data['selling_price']),
                "purchase_rate": float(item_data.get('cost_price', 0)),
                "description": item_data.get('description', ''),
                "initial_stock": float(item_data['quantity']),
                "initial_stock_rate": float(item_data.get('cost_price', 0))
            }
            
            current_app.logger.info(f"Updating item details: {update_data}")
            
            response = requests.put(
                f"{self.base_url}/items/{item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=update_data
            )
            
            if response.status_code == 200:
                current_app.logger.info(f"Successfully updated item details in Zoho: {response.json()}")
                return response.json()
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.update_item_in_zoho(item_id, item_data)
            
            current_app.logger.error(f"Failed to update item in Zoho: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error updating item in Zoho: {str(e)}")
            return None

    def delete_item_in_zoho(self, zoho_item_id: str) -> bool:
        """Mark an item as inactive in Zoho."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return False
        
        try:
            # First check if the item exists in Zoho
            response = requests.get(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            current_app.logger.info(f"Checking item existence in Zoho. Status: {response.status_code}")
            
            if response.status_code == 404:
                # Item doesn't exist in Zoho, consider it deleted
                current_app.logger.info(f"Item {zoho_item_id} not found in Zoho, considering it deleted")
                return True
            
            if response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.delete_item_in_zoho(zoho_item_id)
            
            if response.status_code != 200:
                current_app.logger.error(f"Failed to check item existence in Zoho: {response.status_code} - {response.text}")
                return False
            
            # If item exists, mark it as inactive
            response = requests.put(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    "status": "inactive"
                }
            )
            
            current_app.logger.info(f"Marking item as inactive. Status: {response.status_code}")
            
            if response.status_code == 200:
                current_app.logger.info(f"Successfully marked item {zoho_item_id} as inactive in Zoho")
                return True
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.delete_item_in_zoho(zoho_item_id)
            
            current_app.logger.error(f"Failed to mark item as inactive in Zoho: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error marking item as inactive in Zoho: {str(e)}")
            return False

    def check_and_update_expired_items(self, user: User) -> bool:
        """Check for expired items and update their status in Zoho."""
        try:
            # Get all items for the user
            items = Item.query.filter_by(user_id=user.id).all()
            current_date = datetime.now().date()
            
            for item in items:
                if not item.zoho_item_id or not item.expiry_date:
                    continue
                    
                # Check if item has expired
                if item.expiry_date.date() <= current_date:
                    # Update local status first
                    item.update_status(force_update=True)
                    
                    # Update item status in Zoho to inactive
                    self.update_item_in_zoho(item.zoho_item_id, {
                        "name": item.name,
                        "unit": item.unit,
                        "rate": item.selling_price,
                        "stock_on_hand": item.quantity,
                        "description": item.description or "",
                        "expiry_date": item.expiry_date.strftime('%Y-%m-%d'),
                        "status": "inactive"
                    })
            
            return True
            
        except Exception as e:
            current_app.logger.error(f"Error checking expired items: {str(e)}")
            return False

    def get_item_status(self, zoho_item_id: str) -> Optional[str]:
        """Get the status of an item in Zoho Inventory."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('item', {}).get('status')
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.get_item_status(zoho_item_id)
            
            current_app.logger.error(f"Failed to get item status from Zoho: {response.status_code} - {response.text}")
            return None
            
        except Exception as e:
            current_app.logger.error(f"Error getting item status from Zoho: {str(e)}")
            return None

    def logout(self):
        """Logout from Zoho and clear access token."""
        try:
            # Clear the tokens from the user record
            self.user.zoho_access_token = None
            self.user.zoho_refresh_token = None
            self.user.zoho_token_expires_at = None
            self.user.zoho_organization_id = None
            db.session.commit()
            return True
        except Exception as e:
            current_app.logger.error(f"Error logging out from Zoho: {str(e)}")
            return False

    def update_item_status_in_zoho(self, zoho_item_id: str, status: str) -> bool:
        """Update item status in Zoho."""
        access_token = self.get_access_token()
        if not access_token:
            current_app.logger.error("No access token available")
            return False
            
        try:
            current_app.logger.info(f"Updating item {zoho_item_id} status to {status} in Zoho")
            
            response = requests.put(
                f"{self.base_url}/items/{zoho_item_id}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json={
                    'status': status
                }
            )
            
            if response.status_code == 200:
                current_app.logger.info(f"Successfully updated item {zoho_item_id} status to {status}")
                return True
            elif response.status_code == 401:
                current_app.logger.info("Token expired, attempting to refresh")
                if self.refresh_token():
                    return self.update_item_status_in_zoho(zoho_item_id, status)
            
            current_app.logger.error(f"Failed to update item status in Zoho: {response.status_code} - {response.text}")
            return False
            
        except Exception as e:
            current_app.logger.error(f"Error updating item status in Zoho: {str(e)}")
            return False

    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """Make a request to the Zoho API."""
        access_token = self.get_access_token()
        if not access_token:
            return None
            
        try:
            response = requests.request(
                method,
                f"{self.base_url}{endpoint}",
                headers={
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                },
                json=data,
                params=params
            )
            
            if response.status_code == 401:
                current_app.logger.error("Unauthorized - token may be invalid")
                return None
                
            if response.status_code != 200:
                current_app.logger.error(f"Request failed: {response.status_code} - {response.text}")
                return None
                
            return response.json()
            
        except Exception as e:
            current_app.logger.error(f"Error making request: {str(e)}")
            return None 