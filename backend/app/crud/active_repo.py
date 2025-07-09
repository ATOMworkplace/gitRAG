# app/crud/active_repo.py
from sqlalchemy.orm import Session
from app.models.active_repo import ActiveRepo

def set_active_repo(db: Session, user_id: str, repo_url: str):
    obj = db.query(ActiveRepo).filter_by(user_id=user_id).one_or_none()
    if obj:
        obj.repo_url = repo_url
    else:
        obj = ActiveRepo(user_id=user_id, repo_url=repo_url)
        db.add(obj)
    db.commit()
    return obj

def get_active_repo(db: Session, user_id: str):
    obj = db.query(ActiveRepo).filter_by(user_id=user_id).one_or_none()
    return obj.repo_url if obj else None

def delete_active_repo(db: Session, user_id: str):
    obj = db.query(ActiveRepo).filter_by(user_id=user_id).one_or_none()
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False
