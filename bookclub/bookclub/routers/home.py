from typing import Annotated, Optional

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from models import models
from requests import Session
from settings import settings
from utils.auth import get_current_active_user
from utils.email import send_email
from utils.leaderboard import generate_leaderboard

router = APIRouter(tags=["home"])

CURRENT_YEAR = settings.CURRENT_YEAR


@router.get("/login", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")


@router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie("access_token")
    response.delete_cookie("user_id")
    return response


@router.get("/signup", response_class=HTMLResponse)
async def signup(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")


@router.post("/signup", response_class=JSONResponse)
async def signup_request(
    request: Request,
    email: str = Form(...),
    reason: str = Form(...),
    friend: str = Form(None),
):
    email_body = f"""
    New Signup Request:
    
    Email: {email}
    Reason: {reason}
    Friend: {friend if friend else "N/A"}
    
    Please look into this request and add user to the system.
    """
    twillio_response = send_email("New Signup Request", email_body)
    if isinstance(twillio_response, Exception):
        return JSONResponse(content={"message": "Failed to send email"}, status_code=500)

    return JSONResponse(
        content={"message": "Signup request received, you will get an email soon!"},
        status_code=201,
    )


@router.get("/")
async def bookclub(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse("home.html", {"request": request, "user_id": current_user.id})


@router.get("/all_users")
async def all_users(
    db: Session = Depends(get_db),
    year: Optional[int] = Query(settings.CURRENT_YEAR),
):
    return generate_leaderboard(db, year)


@router.get("/latest_submissions", response_class=JSONResponse)
def latest_submissions(request: Request, db: Session = Depends(get_db)):
    latest_submissions = crud.get_latest_submissions(db)
    for submission in latest_submissions:
        user_name = crud.get_user(db, submission.user_id).username
        submission.__dict__["username"] = user_name
    return latest_submissions
