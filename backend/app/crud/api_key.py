# app/crud/api_key.py
from sqlalchemy.orm import Session
from app.models import APIKey
from app.services.encryption_service import encrypt_key, decrypt_key

def upsert_api_key(db: Session, user_id: str, key: str):
    """
    Encrypts the API key before saving it to the database.
    """
    encrypted_api_key = encrypt_key(key) # Encrypt the key
    
    obj = db.query(APIKey).filter_by(user_id=user_id).one_or_none()
    if obj:
        obj.key = encrypted_api_key
    else:
        obj = APIKey(user_id=user_id, key=encrypted_api_key)
        db.add(obj)
    db.commit()
    return obj

def delete_api_key(db: Session, user_id: str):
    obj = db.query(APIKey).filter_by(user_id=user_id).one_or_none()
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False

def get_api_key(db: Session, user_id: str):
    """
    Fetches the key from the database and decrypts it before returning.
    """
    obj = db.query(APIKey).filter_by(user_id=user_id).one_or_none()
    if obj and obj.key:
        return decrypt_key(obj.key) # Decrypt the key
    return None