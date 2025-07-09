from .user import User
from .api_key import APIKey
from .chat import ChatMessage
from sqlalchemy.orm import relationship

User.api_key = relationship("APIKey", uselist=False, back_populates="user")
User.chat_messages = relationship("ChatMessage", back_populates="user")
