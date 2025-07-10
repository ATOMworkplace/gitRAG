
from fastapi import FastAPI
from app.core.oauth import init_oauth
from app.routers.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware # Import SessionMiddleware
from app.routers import ai, repo
from app.utils.db import engine, Base
import os # Import os to get secret key from environment variables

app = FastAPI()
init_oauth(app)
Base.metadata.create_all(bind=engine)

# IMPORTANT: Add SessionMiddleware to handle user login sessions
# This must be added BEFORE the routers.
# The secret key is essential for signing the session cookie.
# It's best practice to load this from an environment variable.
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get('SESSION_SECRET_KEY'),
    https_only=True,  # Ensures cookie is only sent over HTTPS
    same_site="none"    # Required for cross-domain cookies
)

# Add CORS middleware to allow your frontend to communicate with this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://git-rag.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include ALL routers under `/api`
app.include_router(auth_router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(repo.router, prefix="/api")


@app.get('/', methods=['GET', 'HEAD'])
async def root():
    return {'message': 'RAG AI Chatbot Backend'}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host='0.0.0.0', port=8000, reload=True)
