#app/core/oauth.py
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from .config import SESSION_SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET

oauth = OAuth()

def init_oauth(app: FastAPI):
    """Install session middleware and register OAuth clients."""
    # Session for OAuth state and storing user
    app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET_KEY)

    # Google OAuth
    oauth.register(
        name='google',
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile',
            # 'prompt': 'consent',  # (optional) can force Google to always ask account
            # 'access_type': 'offline',  # (optional) for refresh_token
        },
    )
    # GitHub OAuth
    oauth.register(
        name='github',
        client_id=GITHUB_CLIENT_ID,
        client_secret=GITHUB_CLIENT_SECRET,
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )
