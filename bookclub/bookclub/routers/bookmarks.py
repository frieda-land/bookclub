from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse, RedirectResponse
from models.models import User
from requests import Session
from utils.auth import get_current_active_user

router = APIRouter(prefix="/bookmarks", tags=["bookmarks"])


@router.get("/")
def bookmarks(
    request: Request,
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(
        request=request,
        name="bookmarked.html",
        context={"user_id": current_user.id},
    )


@router.get("/{user_id}")
def get_bookmarks(user_id: str, db: Session = Depends(get_db)):
    bookmarks = crud.get_favourites(db, int(user_id))
    transformed = [
        {
            "category_name": crud.get_category_by_number(db, bookmark.category_id).title,
            "author_title": bookmark.book_info.split(" - ")[0],
            "bookmark_id": bookmark.id,
        }
        for bookmark in bookmarks
    ]
    return transformed


@router.delete("/{bookmark_id}")
def delete_bookmark(bookmark_id: str, db: Session = Depends(get_db)):
    try:
        crud.remove_bookmark_by_id(db, int(bookmark_id))
    except Exception:
        return JSONResponse(
            content={"message": "Failed to remove bookmark."},
            status_code=400,
        )
