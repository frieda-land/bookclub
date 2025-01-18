from datetime import timedelta
from urllib.parse import urlencode

import httpx
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from models import models
from requests import Session
from schemas import schema
from settings import settings
from utils.auth import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

AUTHORIZE_URL_GOOGLE = settings.AUTHORIZE_URL_GOOGLE
GOOGLE_CLIENT_ID = settings.GOOGLE_CLIENT_ID
GOOGLE_CLIENT_SECRET = settings.GOOGLE_CLIENT_SECRET
GOOGLE_REDIRECT_URI = settings.GOOGLE_REDIRECT_URI
GOOGLE_USER_INFO_URL = settings.GOOGLE_USER_INFO_URL
ALLOWED_EMAILS = settings.ALLOWED_EMAILS
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


def get_authorization_url():
    params = {
        "response_type": "code",
        "client_id": GOOGLE_CLIENT_ID,
        "redirect_uri": "http://localhost:8000/auth/google",
        "scope": "openid profile email",
        "access_type": "offline",
    }
    return f"{AUTHORIZE_URL_GOOGLE}?{urlencode(params)}"


@router.get("/google_auth_url")
async def login(request: Request):
    url = get_authorization_url()
    return {"authorization_url": url}


@router.get("/google")
async def auth_google(request: Request, code: str, db: Session = Depends(get_db)):
    if not code:
        raise HTTPException(status_code=400, detail="Code not provided")
    # todo: move to settings
    token_url = "https://accounts.google.com/o/oauth2/token"
    data = {
        "code": code,
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "redirect_uri": GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            token_response = response.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Failed to exchange code for token")

    access_token = token_response.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="No access token returned")

    async with httpx.AsyncClient() as client:
        response = await client.get(GOOGLE_USER_INFO_URL, headers={"Authorization": f"Bearer {access_token}"})
        response.raise_for_status()
        user_info = response.json()

    user_google_email = user_info.get("email")
    user_google_name = user_info.get("name")
    user = db.query(models.User).filter(models.User.email == user_google_email).first()

    if not user and user_google_email in ALLOWED_EMAILS:
        try:
            user = crud.create_user(
                db,
                schema.UserCreate(username=user_google_name, email=user_google_email),
            )
        except Exception:
            # add logging
            return RedirectResponse(url="/signup?message=failed_to_create_user")
    elif not user:
        # add logging
        return RedirectResponse(url="/signup?message=invalid_user")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user_google_email}, expires_delta=access_token_expires)
    response = RedirectResponse(url="/")

    response.set_cookie(key="access_token", value=access_token)
    response.set_cookie(key="user_id", value=str(user.id))

    return response
