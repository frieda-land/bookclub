from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from requests import Session
from schemas.schema import SubmittedBook
from utils.auth import get_current_active_user
from utils.categories import submitted_books

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


@router.post("/challenge")
def submit_previous_challenges(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    created_challenges = []
    for year, user in submitted_books.items():
        for user, books in user.items():
            try:
                user = crud.get_user_by_email(db, user)
                for book in books:
                    try:
                        original_number, author, book_name, rating = (
                            book["original_number"],
                            book["author"],
                            book["book_name"],
                            book["rating"],
                        )
                    except KeyError as e:
                        return {"status": "Failed", "error": f"Missing or wrong key: {e}"}
                    created_challenge = crud.create_entry_for_user(
                        db,
                        int(user.id),
                        int(original_number),
                        year,
                        SubmittedBook(author=author, name=book_name, rating=int(rating)),
                    )
                    if not created_challenge:
                        continue
                    created_challenges.append(created_challenge)
            except Exception:
                return {
                    "status": "Failed",
                    "created_categories": created_challenges,
                    "number_of_categories": len(created_challenges),
                }
    return {
        "status": "Success",
        "created_categories": created_challenges,
        "number_of_categories": len(created_challenges),
    }
