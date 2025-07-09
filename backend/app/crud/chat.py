# app/crud/chat.py
from sqlalchemy.orm import Session
from app.models import ChatMessage

def log_chat(db: Session, namespace: str, role: str, content: str, user_id: str):
    msg = ChatMessage(
        namespace=namespace,
        role=role,
        content=content,
        user_id=user_id
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg

def delete_chat_namespace(db: Session, namespace: str):
    db.query(ChatMessage).filter_by(namespace=namespace).delete()
    db.commit()


def get_chat_messages_for_namespace(db: Session, namespace: str):
    return db.query(ChatMessage).filter_by(namespace=namespace).order_by(ChatMessage.created_at.asc()).all()

def delete_chat_message(db: Session, msg_id: int, user_id: str):
    msg = db.query(ChatMessage).filter_by(id=msg_id, user_id=user_id).first()
    if msg:
        db.delete(msg)
        db.commit()
        return True
    return False
