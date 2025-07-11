from fastapi import FastAPI
from app.core.oauth import init_oauth
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware  
from app.routers import ai, repo
from app.utils.db import engine, Base
import os  

app = FastAPI()
print("[DEBUG][main.py] FastAPI app created.")
init_oauth(app)
print("[DEBUG][main.py] OAuth initialized.")
Base.metadata.create_all(bind=engine)
print("[DEBUG][main.py] Database tables created.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://git-rag.vercel.app",
        "https://www.git-rag.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("[DEBUG][main.py] CORS middleware configured.")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get('SESSION_SECRET_KEY'),
    https_only=True,   
    same_site="none"     
)
print("[DEBUG][main.py] Session middleware configured.")

app.include_router(auth_router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(repo.router, prefix="/api")
print("[DEBUG][main.py] Routers included.")

@app.get('/')
async def root():
    print("[DEBUG][main.py] / endpoint hit.")
    return {'message': 'RAG AI Chatbot Backend'}

if __name__ == '__main__':
    import uvicorn
    print("[DEBUG][main.py] Starting app with uvicorn.")
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
