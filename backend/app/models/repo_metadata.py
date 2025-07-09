# app/models/repo_metadata.py

from sqlalchemy import Column, String, Text, DateTime, func
from app.utils.db import Base

class RepoMetadata(Base):
    __tablename__ = "repo_metadata"
    repo_url = Column(String, primary_key=True)
    file_tree_json = Column(Text, nullable=False)
    analytics_json = Column(Text, nullable=True)
    dependency_graph_json = Column(Text, nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
