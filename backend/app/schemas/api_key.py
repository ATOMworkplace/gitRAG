# app/schemas/api_key.py
from pydantic import BaseModel

class APIKeyCreate(BaseModel):
    openai_api_key: str
