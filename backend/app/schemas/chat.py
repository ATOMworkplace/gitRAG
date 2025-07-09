from pydantic import BaseModel
from typing import List
from datetime import datetime

# Used for /ai/chat
class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    result: str

# Used for chat history output
class ChatMessageOut(BaseModel):
    role: str
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageOut]
