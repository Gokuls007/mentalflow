from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from cryptography.hazmat.backends import default_backend
import base64
from app.config import settings

class DataEncryption:
    """Encrypt sensitive data at rest using Fernet (AES-128 in CBC mode, HMAC-SHA256)."""
    
    def __init__(self, master_key: str):
        """Initialize with master encryption key."""
        # Derive encryption key from master key using PBKDF2 for added security
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'mentalflow_pii_salt_v1', # In production, this should be a stable secret
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(master_key.encode())
        )
        self.cipher = Fernet(key)
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt string to base64 encoded ciphertext."""
        if not plaintext:
            return ""
        return self.cipher.encrypt(plaintext.encode()).decode()
    
    def decrypt(self, ciphertext: str) -> str:
        """Decrypt base64 encoded ciphertext back to plaintext."""
        if not ciphertext:
            return ""
        return self.cipher.decrypt(ciphertext.encode()).decode()

# Initialize global encryption service
encryption_service = DataEncryption(settings.ENCRYPTION_KEY)
