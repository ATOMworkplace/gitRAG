# app/schemas/api_key.py
from pydantic import BaseModel

class APIKeyCreate(BaseModel):
    openai_api_key: str

# Used by /api/ai/get_api_key
class GetKeyRequest(BaseModel):
    user_id: str
    provider: str

# Used by /api/ai/validate_api_key
class ValidateKeyRequest(BaseModel):
    user_id: str
    provider: str
    api_key: str

# Used by /api/ai/delete_api_key
class DeleteKeyRequest(BaseModel):
    user_id: str
    provider: str

# Used by /api/ai/get_openai_key
class GetKeyRequestLegacy(BaseModel):
    user_id: str

# Used by /api/ai/validate_openai_key
class ValidateKeyRequestLegacy(BaseModel):
    user_id: str
    openai_api_key: str

# Used by /api/ai/delete_openai_key
class DeleteKeyRequestLegacy(BaseModel):
    user_id: str