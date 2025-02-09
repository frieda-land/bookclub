import json
from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from models import models
from requests import Session
from schemas.schema import ChallengeCategoryCreate, NewsletterUser
from settings import settings
from utils.auth import get_current_active_user
from utils.categories import create_single_category
from utils.email import send_welcome_to_newsletter

router = APIRouter(prefix="/profile", tags=["profile"])

CURRENT_YEAR = settings.CURRENT_YEAR


@router.get("/", response_class=HTMLResponse)
async def profile(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    trophies = {
        "monthly": [],
        "yearly": [],
    }
    for trophy in current_user.trophies:
        if trophy.kind == models.TrophyType.MONTHLY:
            trophies["monthly"].append(
                {
                    "year": trophy.year,
                    "month": crud.month_names[trophy.month - 1],
                    "number_of_books_read": trophy.number_of_books_read,
                }
            )
        else:
            trophies["yearly"].append({"year": trophy.year, "number_of_books_read": trophy.number_of_books_read})
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user_id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "year": CURRENT_YEAR,
            "newsletter_email": current_user.newsletter_email_address,
            "trophies": trophies,
        },
    )


@router.post("/custom_category", response_class=HTMLResponse)
async def profile_custom_category(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    category: str = Form(...),
):
    category = ChallengeCategoryCreate(title=category)
    try:
        create_single_category(db, category, current_user.id)
    except Exception as e:
        return templates.TemplateResponse(
            request=request,
            name="profile.html",
            context={
                "user_id": current_user.id,
                "email": current_user.email,
                "username": current_user.username,
                "year": CURRENT_YEAR,
                "newsletter_email": current_user.newsletter_email_address,
                "error": e.detail,
            },
        )
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
        context={
            "user_id": current_user.id,
            "email": current_user.email,
            "username": current_user.username,
            "year": CURRENT_YEAR,
            "newsletter_email": current_user.newsletter_email_address,
        },
    )


@router.get("/custom_category/{user_id}")
def my_books_custom_category(user_id: str, year: int = CURRENT_YEAR, db: Session = Depends(get_db)):
    custom_categories = crud.get_custom_categories(db, int(user_id))
    return [custom.title for custom in custom_categories] if custom_categories else []


@router.delete("/custom_category/{user_id}/category/{category_title}")
def delete_custom_category(request: Request, user_id: str, category_title: str, db: Session = Depends(get_db)):
    try:
        submitted_books = crud.submitted_books_for_category_by_title(db, category_title)
        if submitted_books:
            return JSONResponse(
                content={"message": "Cannot delete category as it has submissions."},
                status_code=403,
            )
        crud.remove_category_by_title(db, category_title, int(user_id))
    except Exception:
        return JSONResponse(
            content={"message": "Failed to remove custom category."},
            status_code=400,
        )


@router.post("/subscribe")
async def subscribe_to_newsletter(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        crud.subscribe_user_to_newsletter(db, current_user, email)
    except Exception:
        return JSONResponse(
            content={"message": "Failed to subscribe to newsletter."},
            status_code=400,
        )
    subscriber = NewsletterUser(newsletter_email_address=email, username=current_user.username, user_id=current_user.id)
    try:
        send_welcome_to_newsletter(db, subscriber)
    except Exception:
        # todo add exponential backoff
        return JSONResponse(
            content={"message": "Added user but failed to send welcome email."},
            status_code=400,
        )


@router.post("/unsubscribe")
async def unsubscribe_to_newsletter(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    try:
        crud.unsubscribe_user_from_newsletter(db, current_user)
    except Exception:
        return JSONResponse(
            content={"message": "Failed to unsubscribe to newsletter."},
            status_code=400,
        )
