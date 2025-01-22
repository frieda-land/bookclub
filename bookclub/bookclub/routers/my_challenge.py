from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from models import models
from requests import Session
from schemas.schema import SubmittedBook
from settings import settings
from utils.auth import get_current_active_user

router = APIRouter(prefix="/my_challenge", tags=["challenge"])

CURRENT_YEAR = settings.CURRENT_YEAR


@router.get("/", response_class=HTMLResponse)
async def challenge(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse("challenge.html", {"request": request, "user_id": current_user.id})


@router.post("/")
def submit_book(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    author: str = Form(...),
    book_name: str = Form(...),
    category: str = Form(...),
    rating: str = Form(...),
    db: Session = Depends(get_db),
    year: int = CURRENT_YEAR,
):
    try:
        crud.create_entry_for_user(
            db,
            int(current_user.id),
            int(category),
            year,
            SubmittedBook(author=author, name=book_name, rating=int(rating)),
        )
    except Exception:
        print(Exception)
        return templates.TemplateResponse(
            request=request,
            name="challenge.html",
            context={"user_id": current_user.id},
        )
    return templates.TemplateResponse(
        request=request,
        name="challenge.html",
        context={"user_id": current_user.id},
    )


@router.get("/books/{user_id}")
def my_books(user_id: str, year: int = CURRENT_YEAR, db: Session = Depends(get_db)):
    books = crud.get_books_for_user_for_year(db, user_id, year)
    transformed_books = []
    for book in books:
        b = crud.get_category_by_number(db, book.category_id)
        transformed_books.append(
            {
                "category_id": b.original_number,
                "title": b.title,
                "author": book.author,
                "book_name": book.book_name,
            }
        )
    return transformed_books


@router.delete("/books/{user_id}/category/{category_id}")
def delete_book(
    request: Request,
    user_id: str,
    category_id: str,
    db: Session = Depends(get_db),
):
    # TODO try except type casting
    crud.delete_entry_for_user(db, int(user_id), int(category_id))

    return templates.TemplateResponse(
        request=request,
        name="challenge.html",
        context={"user_id": user_id},
    )


@router.get("/all_unused_categories/{user_id}")
async def all_unused_categories(
    user_id: str,
    db: Session = Depends(get_db),
    year: int = CURRENT_YEAR,
):
    all_categories = [
        {
            "original_number": category.original_number,
            "title": category.title,
        }
        for category in crud.get_unused_categories(db, int(user_id), year)
    ]
    return sorted(all_categories, key=lambda item: item["original_number"], reverse=False)
