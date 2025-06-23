import bcrypt
import base64
import os
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Global encryption key (in production, this should be stored securely)
_encryption_key = None

def get_encryption_key() -> bytes:
    """Get or generate the encryption key for Zoho credentials"""
    global _encryption_key
    if _encryption_key is None:
        # In production, this should be loaded from environment variables
        # For now, we'll generate a key based on a master password
        master_password = os.getenv('ZOHO_MASTER_PASSWORD', 'default_master_password_change_in_production')
        
        # Generate a key from the master password
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'zoho_credential_salt',  # In production, use a random salt
            iterations=100000,
        )
        _encryption_key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    
    return _encryption_key

def hash_zoho_credential(credential: str) -> Tuple[str, str]:
    """
    Encrypt a Zoho credential using Fernet.
    
    Args:
        credential: The plain text credential to encrypt
        
    Returns:
        Tuple of (encrypted_credential, salt)
    """
    try:
        # Get the encryption key
        key = get_encryption_key()
        fernet = Fernet(key)
        
        # Encrypt the credential
        encrypted = fernet.encrypt(credential.encode('utf-8'))
        
        # Convert to base64 for storage
        encrypted_b64 = base64.b64encode(encrypted).decode('utf-8')
        
        # Generate a random salt for this credential
        salt = base64.b64encode(os.urandom(16)).decode('utf-8')
        
        return encrypted_b64, salt
        
    except Exception as e:
        print(f"Error encrypting credential: {e}")
        raise

def verify_zoho_credential(encrypted_credential: str, salt: str) -> Optional[str]:
    """
    Decrypt a Zoho credential.
    
    Args:
        encrypted_credential: The encrypted credential from database
        salt: The salt used for encryption (not used in current implementation)
        
    Returns:
        The decrypted credential if successful, None otherwise
    """
    try:
        # Get the encryption key
        key = get_encryption_key()
        fernet = Fernet(key)
        
        # Convert from base64
        encrypted_bytes = base64.b64decode(encrypted_credential.encode('utf-8'))
        
        # Decrypt the credential
        decrypted = fernet.decrypt(encrypted_bytes)
        
        return decrypted.decode('utf-8')
        
    except Exception as e:
        print(f"Error decrypting credential: {e}")
        return None

def generate_secure_token() -> str:
    """
    Generate a secure random token.
    
    Returns:
        A secure random token
    """
    return base64.b64encode(os.urandom(32)).decode('utf-8')

def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    Args:
        password: The plain text password
        
    Returns:
        The hashed password
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: The plain text password
        hashed_password: The hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')) 