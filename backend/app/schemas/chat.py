# app/schemas/chat.py
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Used for /ai/chat
class ChatRequest(BaseModel):
    message: str
    user_id: str
    provider: Optional[str] = None  

class ChatResponse(BaseModel):
    result: str

# Used for chat history output
class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True  

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageOut]