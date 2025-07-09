# app/crud/api_key.py
from sqlalchemy.orm import Session
from app.models import APIKey

def upsert_api_key(db: Session, user_id: str, key: str):
    obj = db.query(APIKey).filter_by(user_id=user_id).one_or_none()
    if obj:
        obj.key = key
    else:
        obj = APIKey(user_id=user_id, key=key)
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
    obj = db.query(APIKey).filter_by(user_id=user_id).one_or_none()
    return obj.key if obj else None
