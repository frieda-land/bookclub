from typing import Annotated

from config import templates
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from utils.auth import get_current_active_user

router = APIRouter(prefix="/previous_challenges", tags=["challenges"])


@router.get("/", response_class=HTMLResponse)
async def all_challenges(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(
        request=request,
        name="all_challenges.html",
        context={"user_id": current_user.id},
    )


@router.get("/leaderboard/{year}", response_class=HTMLResponse)
async def leaderboard_for_year(
    request: Request,
    year: int,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(
        "leaderboard.html",
        {"request": request, "user_id": current_user.id, "year": year},
    )
