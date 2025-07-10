import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

# Load environment variables for the encryption key
load_dotenv()

# Load the master encryption key from environment variables
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables")

# Initialize the Fernet cipher suite
cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_key(plaintext_key: str) -> str:
    """Encrypts a plaintext key."""
    if not plaintext_key:
        return ""
    encrypted_key = cipher_suite.encrypt(plaintext_key.encode())
    return encrypted_key.decode()

def decrypt_key(encrypted_key: str) -> str:
    """Decrypts an encrypted key."""
    if not encrypted_key:
        return ""
    try:
        decrypted_key = cipher_suite.decrypt(encrypted_key.encode())
        return decrypted_key.decode()
    except Exception:
        # If decryption fails (e.g., key is invalid or not encrypted),
        # handle it gracefully. Here, we'll assume it might be an old
        # unencrypted key and return it as is, but you could also raise an error.
        return encrypted_key