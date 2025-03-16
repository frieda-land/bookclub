import json
from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from models import models
from utils.auth import get_current_active_user

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/")
def admin(request: Request, current_user: Annotated[models.User, Depends(get_current_active_user)], db=Depends(get_db)):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
        },
    )
