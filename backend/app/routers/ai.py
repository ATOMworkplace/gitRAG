# app/routers/ai.py

from fastapi import APIRouter, HTTPException, Body, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.rag_service import chat_with_rag, validate_openai_key
from app.utils.db import get_db
from app.crud.api_key import upsert_api_key, delete_api_key, get_api_key
from app.crud.active_repo import get_active_repo
from app.crud.chat import (
    log_chat,
    get_chat_messages_for_namespace,
    delete_chat_message,    
)
from app.schemas.chat import (
    ChatRequest, ChatResponse, ChatHistoryResponse
)

router = APIRouter(prefix="/ai", tags=["AI"])

# Request/response models
class GetChatHistoryRequest(BaseModel):
    user_id: str

class GetKeyRequest(BaseModel):
    user_id: str

class OpenAIKeyRequest(BaseModel):
    user_id: str
    openai_api_key: str

class DeleteKeyRequest(BaseModel):
    user_id: str

# Fetch chat history for the user's current repo
@router.post("/get_chat_history", response_model=ChatHistoryResponse)
async def get_chat_history_endpoint(
    body: GetChatHistoryRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        repo_url = get_active_repo(db, body.user_id)
        if not repo_url:
            raise HTTPException(status_code=400, detail="No active repo set for this user. Please ingest a repo first.")

        namespace = f"{body.user_id}_{repo_url.rstrip('/').split('/')[-1]}"
        messages = get_chat_messages_for_namespace(db, namespace)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get OpenAI API Key (masked)
@router.post("/get_openai_key")
async def get_openai_key_endpoint(
    body: GetKeyRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        key = get_api_key(db, body.user_id)
        if key:
            masked = "****" + key[-4:]
            return {"exists": True, "masked_key": masked}
        else:
            return {"exists": False, "masked_key": ""}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Validate and set OpenAI API Key
@router.post("/validate_openai_key")
async def validate_openai_key_endpoint(
    body: OpenAIKeyRequest,
    db: Session = Depends(get_db)
):
    try:
        if not body.openai_api_key or not isinstance(body.openai_api_key, str):
            return {"valid": False, "error": "openai_api_key missing or invalid"}
        valid = validate_openai_key(body.openai_api_key)
        if valid:
            upsert_api_key(db, body.user_id, body.openai_api_key)
        return {"valid": valid}
    except Exception as e:
        return {"valid": False, "error": str(e)}

# Delete OpenAI API Key
@router.delete("/delete_openai_key")
async def delete_openai_key_endpoint(
    body: DeleteKeyRequest,
    db: Session = Depends(get_db)
):
    try:
        deleted = delete_api_key(db, body.user_id)
        if deleted:
            return {"deleted": True}
        else:
            raise HTTPException(status_code=404, detail="API key not found for this user.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Main chat endpoint (creates chat message for user and assistant)
@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    req: ChatRequest,
    db: Session = Depends(get_db)
):
    try:
        openai_api_key = get_api_key(db, req.user_id)
        if not openai_api_key:
            raise HTTPException(status_code=401, detail="No OpenAI API key set for this user.")

        repo_url = get_active_repo(db, req.user_id)
        if not repo_url:
            raise HTTPException(status_code=400, detail="No active repo set for this user. Please ingest a repo first.")

        namespace = f"{req.user_id}_{repo_url.rstrip('/').split('/')[-1]}"
        log_chat(db, namespace, role="user", content=req.message, user_id=req.user_id)
        result = chat_with_rag(req.message, namespace, openai_api_key)
        log_chat(db, namespace, role="assistant", content=result, user_id=req.user_id)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Delete a chat message (by msg id and user id)
@router.delete("/delete_message")
async def delete_message_endpoint(
    msg_id: int = Query(...),
    user_id: str = Query(...),
    db: Session = Depends(get_db)
):
    ok = delete_chat_message(db, msg_id, user_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Message not found or unauthorized.")
    return {"deleted": True}
