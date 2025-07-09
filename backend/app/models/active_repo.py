from sqlalchemy import Column, String, ForeignKey
from app.utils.db import Base

class ActiveRepo(Base):
    __tablename__ = "active_repos"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    repo_url = Column(String, nullable=False)
