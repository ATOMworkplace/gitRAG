from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

load_dotenv()

from app.core.config import BASE_URL, FRONT_END_URL
from app.core.oauth import oauth
from app.utils.db import get_db
from app.crud.user import get_or_create_user
from app.schemas.user import UserInfo

router = APIRouter(tags=["Auth"])

@router.get('/login/{provider}')
async def login(request: Request, provider: str):
    print(f"[DEBUG][auth.py] /login/{provider} endpoint called")
    print(f"[DEBUG][auth.py] BASE_URL: {BASE_URL}")
    print(f"[DEBUG][auth.py] Provider: {provider}")
    if provider not in ('google', 'github'):
        print("[DEBUG][auth.py] Unsupported provider requested")
        raise HTTPException(400, 'Unsupported provider')
    client = getattr(oauth, provider)
    redirect_uri = f"{BASE_URL}/api/auth/{provider}/callback"
    print(f"[DEBUG][auth.py] Redirect URI for OAuth: {redirect_uri}")
    return await client.authorize_redirect(request, redirect_uri)

@router.get('/auth/{provider}/callback')
async def auth_callback(
    request: Request,
    provider: str,
    db: Session = Depends(get_db)
):
    print(f"[DEBUG][auth.py] /auth/{provider}/callback endpoint called")
    print(f"[DEBUG][auth.py] Request cookies on callback: {request.cookies}")
    client = getattr(oauth, provider)
    try:
        token = await client.authorize_access_token(request)
        print(f"[DEBUG][auth.py] OAuth token received: {token}")
    except OAuthError as e:
        print(f"[DEBUG][auth.py] OAuthError: {e}")
        return RedirectResponse(url='/login/error?message=auth_failed')

    if provider == 'google':
        info = token.get('userinfo')
        print(f"[DEBUG][auth.py] Google userinfo: {info}")
        if not info:
            print("[DEBUG][auth.py] Google userinfo fetch failed.")
            return RedirectResponse(url='/login/error?message=fetch_user_failed')
        user_info = UserInfo(
            id=info['sub'],
            name=info['name'],
            email=info['email'],
            picture=info['picture'],
            provider='google'
        )
    else:  # github
        github_token = os.getenv("GITHUB_TOKEN")
        headers = {'Authorization': f'token {github_token}'} if github_token else {}

        resp = await client.get('user', token=token, headers=headers)
        info = resp.json()
        print(f"[DEBUG][auth.py] GitHub userinfo: {info}")
        email = info.get('email')
        
        if not email:
            emails_resp = await client.get('user/emails', token=token, headers=headers)
            emails = emails_resp.json()
            print(f"[DEBUG][auth.py] GitHub user emails: {emails}")
            email = ""
            for e in emails:
                if e.get("primary") and e.get("verified"):
                    email = e.get("email")
                    break
        user_info = UserInfo(
            id=str(info.get('id')),
            name=info.get('name') or info.get('login'),
            email=email or "",
            picture=info.get('avatar_url'),
            provider='github'
        )
    print(f"[DEBUG][auth.py] Final user_info to save: {user_info}")

    # Upsert into DB and session
    print(f"[DEBUG][auth.py] Saving user to DB and session...")
    get_or_create_user(db, user_info.model_dump())
    request.session['user'] = user_info.model_dump()
    print(f"[DEBUG][auth.py] User session set. Session cookie (set in response): {request.session}")
    print(f"[DEBUG][auth.py] Redirecting to {FRONT_END_URL}/home")
    return RedirectResponse(f"{FRONT_END_URL}/home")

@router.get('/user')
async def get_current_user(request: Request):
    print("[DEBUG][auth.py] /user endpoint called")
    print(f"[DEBUG][auth.py] Request cookies: {request.cookies}")
    user = request.session.get('user')
    if not user:
        print("[DEBUG][auth.py] Not authenticated")
        raise HTTPException(status_code=401, detail='Not authenticated')
    print(f"[DEBUG][auth.py] Returning user: {user}")
    return user

@router.get('/logout')
async def logout(request: Request):
    print("[DEBUG][auth.py] /logout endpoint called")
    print(f"[DEBUG][auth.py] Request cookies: {request.cookies}")
    request.session.pop('user', None)
    print("[DEBUG][auth.py] User logged out from session")
    return {"detail": "Logged out"}
