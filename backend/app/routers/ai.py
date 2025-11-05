# app/routers/ai.py
import os
import re
from typing import Optional
from fastapi import APIRouter, HTTPException, Body, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.services.github_service import list_repo_file_paths
from app.services.rag_service import chat_with_rag, validate_key
from app.utils.db import get_db
from app.crud.api_key import upsert_api_key, delete_api_key, get_api_key_by_provider
from app.crud.active_repo import get_active_repo
from app.crud.chat import log_chat, get_chat_messages_for_namespace, delete_chat_message
from app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse

router = APIRouter(prefix="/ai", tags=["AI"])

class GetChatHistoryRequest(BaseModel):
    user_id: str

class GetKeyRequestOld(BaseModel):
    user_id: str

class OpenAIKeyRequestOld(BaseModel):
    user_id: str
    openai_api_key: str

class DeleteKeyRequestOld(BaseModel):
    user_id: str

class GetKeyRequest(BaseModel):
    user_id: str
    provider: str

class ValidateKeyRequest(BaseModel):
    user_id: str
    provider: str
    api_key: str

class DeleteKeyRequest(BaseModel):
    user_id: str
    provider: str

@router.post("/get_chat_history", response_model=ChatHistoryResponse)
async def get_chat_history_endpoint(
    body: GetChatHistoryRequest = Body(...),
    db: Session = Depends(get_db)
):
    try:
        repo_obj = get_active_repo(db, body.user_id)
        if not repo_obj:
            raise HTTPException(status_code=400, detail="No active repo set for this user. Please ingest a repo first.")
        repo_url = repo_obj.repo_url
        namespace = f"{body.user_id}_{repo_url.rstrip('/').split('/')[-1]}"
        messages = get_chat_messages_for_namespace(db, namespace)
        return {"messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/get_api_key")
async def get_key(body: GetKeyRequest, db: Session = Depends(get_db)):
    key = get_api_key_by_provider(db, body.user_id, body.provider)
    return {"exists": bool(key), "masked_key": ("****" + key[-4:]) if key else ""}

@router.post("/validate_api_key")
async def validate_key_endpoint(body: ValidateKeyRequest, db: Session = Depends(get_db)):
    api_key = body.api_key
    if not api_key or not isinstance(api_key, str):
        return {"valid": False, "error": "api_key missing or invalid"}
    ok = validate_key(body.provider, api_key)
    if ok:
        upsert_api_key(db, body.user_id, body.provider, api_key)
    return {"valid": ok}

@router.delete("/delete_api_key")
async def delete_key_endpoint(body: DeleteKeyRequest, db: Session = Depends(get_db)):
    deleted = delete_api_key(db, body.user_id, body.provider)
    if not deleted:
        raise HTTPException(404, "API key not found for this user & provider.")
    return {"deleted": True}

def _format_tree_from_paths(paths: list[str]) -> str:
    tree = {}
    for p in paths:
        parts = p.split("/")
        cur = tree
        for i, part in enumerate(parts):
            if i == len(parts) - 1:
                cur.setdefault(part, None)
            else:
                cur = cur.setdefault(part, {})
    lines = []
    def walk(node, prefix=""):
        items = sorted(node.items(), key=lambda x: (x[1] is None, x[0].lower()))
        for name, child in items:
            lines.append(prefix + name + ("" if child is None else "/"))
            if isinstance(child, dict):
                walk(child, prefix + "  ")
    walk(tree, "")
    return "\n".join(lines)

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db)):
    repo_obj = get_active_repo(db, req.user_id)
    if not repo_obj:
        raise HTTPException(400, "No active repo set. Please ingest a repo first.")
    repo_url = repo_obj.repo_url
    provider = getattr(req, "provider", None)
    saved_provider = repo_obj.provider if repo_obj.provider else "openai"
    provider = provider or saved_provider

    intent_msg = req.message.strip().lower()
    list_files_re = re.compile(r"(list|show|print|give|display).*?(files|file names|project files|repo files)", re.I)
    show_tree_re = re.compile(r"(show|display|list|print).*?(structure|tree|folder|directory|hierarchy)", re.I)


    if list_files_re.search(intent_msg) or show_tree_re.search(intent_msg):
        parts = repo_url.rstrip("/").split("/")
        owner, repo = parts[-2], parts[-1]
        github_token = os.getenv("GITHUB_TOKEN")
        try:
            paths = list_repo_file_paths(owner, repo, github_token=github_token)
        except Exception as e:
            raise HTTPException(500, f"Failed to list repo files: {e}")
        if show_tree_re.search(intent_msg):
            result_text = _format_tree_from_paths(paths)
        else:
            result_text = "\n".join(sorted(paths))
        namespace = f"{req.user_id}_{repo_url.rstrip('/').split('/')[-1]}"
        log_chat(db, namespace, role="user", content=req.message, user_id=req.user_id)
        log_chat(db, namespace, role="assistant", content=result_text, user_id=req.user_id)
        return {"result": result_text}

    api_key = get_api_key_by_provider(db, req.user_id, provider)
    if not api_key:
        raise HTTPException(401, f"No {provider} API key set for this user.")
    namespace = f"{req.user_id}_{repo_url.rstrip('/').split('/')[-1]}"
    log_chat(db, namespace, role="user", content=req.message, user_id=req.user_id)
    result = chat_with_rag(req.message, namespace, provider, api_key)
    log_chat(db, namespace, role="assistant", content=result, user_id=req.user_id)
    return {"result": result}

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
