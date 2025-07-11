from fastapi import FastAPI, Request
from app.core.oauth import init_oauth
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routers import ai, repo
from app.utils.db import engine, Base
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import os

app = FastAPI()

# 1. Mount static files (React build)
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="static")
print("[DEBUG][main.py] FastAPI app created.")

# 2. Init everything else
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
        "https://gitrag-fo9z.onrender.com",  # Add your Render.com URL!
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

# 3. SPA fallback for React Router: serve index.html for any non-API 404
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc):
    # For API endpoints, return JSON 404
    if request.url.path.startswith("/api"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    # For everything else, try to serve React index.html
    index_path = os.path.join("frontend", "dist", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return JSONResponse({"detail": "Not Found"}, status_code=404)

# (Optional) Remove the root route if not needed; SPA fallback handles "/"
# @app.get('/')
# async def root():
#     print("[DEBUG][main.py] / endpoint hit.")
#     return {'message': 'RAG AI Chatbot Backend'}

if __name__ == '__main__':
    import uvicorn
    print("[DEBUG][main.py] Starting app with uvicorn.")
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
