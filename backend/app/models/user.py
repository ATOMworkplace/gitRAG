# app/models/user.py
from sqlalchemy import Column, String
from app.utils.db import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(String, primary_key=True, index=True)
    name     = Column(String, nullable=False)
    email    = Column(String, index=True)
    picture  = Column(String)
    provider = Column(String, nullable=False)
