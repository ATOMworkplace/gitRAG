# app/crud/active_repo.py
from sqlalchemy.orm import Session
from app.models.active_repo import ActiveRepo

def set_active_repo(db: Session, user_id: str, repo_url: str, provider: str):
    obj = db.query(ActiveRepo).filter(ActiveRepo.user_id==user_id).one_or_none()
    if obj:
        obj.repo_url = repo_url
        obj.provider=provider
    else:
        obj = ActiveRepo(user_id=user_id, repo_url=repo_url, provider=provider)
        db.add(obj)
    db.commit()
    return obj

def get_active_repo(db: Session, user_id: str):
    obj = db.query(ActiveRepo).filter_by(user_id=user_id).one_or_none()
    return obj

def delete_active_repo(db: Session, user_id: str):
    obj = db.query(ActiveRepo).filter_by(user_id=user_id).one_or_none()
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False
