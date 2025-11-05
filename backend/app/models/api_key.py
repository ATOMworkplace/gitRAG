# app/models/api_key.py
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.utils.db import Base

class APIKey(Base):
    __tablename__ = "api_keys"
    id     = Column(Integer, primary_key=True, index=True)
    user_id= Column(String, ForeignKey("users.id"), nullable=False, unique=True)
    provider = Column(String, nullable=False)
    key    = Column(String, nullable=False)
    user   = relationship("User", back_populates="api_key")
