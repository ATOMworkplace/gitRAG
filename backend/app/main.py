from fastapi import FastAPI, Request
from app.core.oauth import init_oauth
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware  
from app.routers import ai, repo
from app.utils.db import engine, Base
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
        "https://www.git-rag.com",
        "https://gitrag-fo9z.onrender.com",  # add your deployed backend/frontend URL here!
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
print("[DEBUG][main.py] CORS middleware configured.")

app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get('SESSION_SECRET_KEY', 'dev_secret_for_local'),  # fallback for local dev
    https_only=True,   
    same_site="none"     
)
print("[DEBUG][main.py] Session middleware configured.")

app.include_router(auth_router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(repo.router, prefix="/api")
print("[DEBUG][main.py] Routers included.")

# Serve static files (React build)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
print("[DEBUG][main.py] StaticFiles mounted.")

# Catch-all route for SPA (serves index.html for all unknown routes except API/static)
@app.get("/{full_path:path}")
async def spa_fallback(request: Request, full_path: str):
    # Prevent interfering with /api routes
    if full_path.startswith("api") or full_path.startswith("assets") or "." in full_path:
        return FileResponse(os.path.join("frontend/dist", full_path))
    # Otherwise serve index.html for React Router
    index_path = os.path.join("frontend/dist", "index.html")
    print(f"[DEBUG][main.py] SPA fallback for: {full_path}, serving index.html")
    return FileResponse(index_path)

if __name__ == '__main__':
    import uvicorn
    print("[DEBUG][main.py] Starting app with uvicorn.")
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
