from datetime import datetime, timedelta, timezone

import jwt
from crud import crud
from fastapi import Depends, Request
from fastapi.responses import RedirectResponse
from main import get_db
from requests import Session
from settings import settings

JWT_ALGORITHM = settings.JWT_ALGORITHM


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt


async def get_current_active_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return RedirectResponse(url="/login?message=expired")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[JWT_ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return RedirectResponse(url="/login?message=invalid_user")
    except jwt.ExpiredSignatureError:
        return RedirectResponse(url="/login?message=expired")
    except jwt.InvalidTokenError:
        return RedirectResponse(url="/login?message=expired")

    user = crud.get_user_by_email(db, email)
    if user is None:
        return RedirectResponse(url="/login?message=invalid_user")
    return user
