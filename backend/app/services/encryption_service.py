import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY not found in environment variables")

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_key(plaintext_key: str) -> str:
    if not plaintext_key:
        return ""
    encrypted_key = cipher_suite.encrypt(plaintext_key.encode())
    return encrypted_key.decode()

def decrypt_key(encrypted_key: str) -> str:
    if not encrypted_key:
        return ""
    try:
        decrypted_key = cipher_suite.decrypt(encrypted_key.encode())
        return decrypted_key.decode()
    except Exception:
        return encrypted_key