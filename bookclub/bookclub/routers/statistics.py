import json
from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from models import models
from utils.auth import get_current_active_user

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/")
def statistics(
    request: Request, current_user: Annotated[models.User, Depends(get_current_active_user)], db=Depends(get_db)
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    group = crud.get_default_group(db, current_user.id)
    chart_data = crud.get_statistics(db, group.id)
    readers_of_the_month = crud.get_reader_of_last_30_days(db, group.id)
    return templates.TemplateResponse(
        "statistics.html",
        {
            "request": request,
            "chartData": json.dumps(chart_data),
            "readers_of_the_month": [reader.__dict__ for reader in readers_of_the_month],
        },
    )
