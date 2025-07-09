# app/models/chat.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from app.utils.db import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id        = Column(Integer, primary_key=True, index=True)
    namespace = Column(String, index=True)       
    role      = Column(String, nullable=False)   
    content   = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 
    user_id   = Column(String, ForeignKey("users.id"))
    user      = relationship("User", back_populates="chat_messages")
