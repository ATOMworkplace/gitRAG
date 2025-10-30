from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.utils.db import get_db
from app.services.email_service import EmailService
import os

router = APIRouter(prefix="/discuss", tags=["Discuss"])

class FeedbackIn(BaseModel):
    name: str
    from_email: str | None = None
    category: str
    title: str
    description: str
    steps: str | None = None
    expected_behavior: str | None = None
    actual_behavior: str | None = None
    browser_info: str | None = None
    additional_info: str | None = None
    time: str | None = None

@router.post("/feedback")
async def submit_feedback(payload: FeedbackIn, db: Session = Depends(get_db)):
    try:
        EmailService.send_feedback(payload.model_dump())
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send feedback: {e}")

class ConfigResponse(BaseModel):
    status: str

@router.get("/config", response_model=ConfigResponse)
async def get_discuss_config():
    return {"status": "ok"}
