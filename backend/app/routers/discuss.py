# app/routers/discuss.py

from fastapi import APIRouter, HTTPException, Body, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.utils.db import get_db
import os

router = APIRouter(prefix="/discuss", tags=["Discuss"])

# Request/response models
class ConfigResponse(BaseModel):
    emailjs_service_id: str
    emailjs_template_id: str
    emailjs_public_key: str

# Get EmailJS configuration
@router.get("/config", response_model=ConfigResponse)
async def get_discuss_config():
    try:
        service_id = os.environ.get('EMAILJS_SERVICE_ID')
        template_id = os.environ.get('EMAILJS_TEMPLATE_ID')
        public_key = os.environ.get('EMAILJS_PUBLIC_KEY')
        
        if not service_id or not template_id or not public_key:
            raise HTTPException(
                status_code=500, 
                detail="EmailJS configuration not found. Please set environment variables."
            )
        
        return {
            "emailjs_service_id": service_id,
            "emailjs_template_id": template_id,
            "emailjs_public_key": public_key
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
