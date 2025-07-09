# app/crud/user.py
from sqlalchemy.orm import Session
from app.models import User

def get_or_create_user(db: Session, user_info: dict):
    user = db.query(User).get(user_info["id"])
    if not user:
        user = User(**user_info)
        db.add(user)
    else:
        for k,v in user_info.items():
            setattr(user, k, v)
    db.commit()
    return user
