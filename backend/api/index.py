# api/index.py
from fastapi import FastAPI
from backend.app.main import app as fastapi_app

# Vercel expects a variable named "app" or "handler"
app = fastapi_app
