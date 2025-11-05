# app/crud/api_key.py
from sqlalchemy.orm import Session
from app.models.api_key import APIKey
from app.services.encryption_service import encrypt_key, decrypt_key


def upsert_api_key(db: Session, user_id: str, provider: str, key: str):
    encrypted_api_key = encrypt_key(key)

    obj = (
        db.query(APIKey)
        .filter(APIKey.user_id == user_id, APIKey.provider == provider)
        .one_or_none()
    )
    if obj:
        obj.key = encrypted_api_key
    else:
        obj = APIKey(user_id=user_id, provider=provider, key=encrypted_api_key)
        db.add(obj)

    db.commit()
    return obj


def delete_api_key(db: Session, user_id: str, provider: str):
    obj = (
        db.query(APIKey)
        .filter(APIKey.user_id == user_id, APIKey.provider == provider)
        .one_or_none()
    )
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False

def get_api_key_by_provider(db: Session, user_id: str, provider: str):
    row = (
        db.query(APIKey)
        .filter(APIKey.user_id == user_id, APIKey.provider == provider)
        .one_or_none()
    )
    
    return decrypt_key(row.key) if row and row.key else None