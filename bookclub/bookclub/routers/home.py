from typing import Annotated, Optional

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from models import models
from requests import Session
from schemas.schema import AllowedEmailCreate, GroupCreate, UserGroupUpdate
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
async def signup(request: Request, db: Session = Depends(get_db)):
    groups = crud.get_all_groups(db)
    return templates.TemplateResponse("signup.html", {"request": request, "groups": groups})


@router.get("/create_group", response_class=HTMLResponse)
async def create_group(request: Request, db: Session = Depends(get_db)):
    challenges = crud.get_all_challenges(db)
    return templates.TemplateResponse("create_group.html", {"request": request, "challenges": challenges})


@router.post("/create_group", response_class=JSONResponse)
async def create_group_request(
    request: Request,
    group_name: str = Form(...),
    email: str = Form(...),
    description: str = Form(None),
    challenge: str = Form(...),
    current_user_id: int = Form(None),
    db: Session = Depends(get_db),
):
    challenge = crud.get_challenge_by_name(db, challenge)
    group = crud.create_group(
        db,
        group=GroupCreate(
            name=group_name,
            description=description,
            challenge_id=challenge.id,
            admin_id=current_user_id,
        ),
    )
    crud.create_allowed_email(db, AllowedEmailCreate(email=email, is_admin_request_for_group_id=group.id))
    if current_user_id:
        group = UserGroupUpdate(user_id=current_user_id, group_id=group.id)
        crud.create_group_membership(db, group)
        return JSONResponse(
            content={"message": "Group successfully created!"},
            status_code=201,
        )
    return JSONResponse(
        content={"message": "Group created, please login!"},
        status_code=201,
    )


@router.post("/signup", response_class=JSONResponse)
async def signup_request(
    request: Request,
    email: str = Form(...),
    group_id: str = Form(...),
    reason: str = Form(None),
):
    email_body = f"""
    New Signup Request:
    
    Email: {email}
    Reason: {reason if reason else "N/A"}
    Group ID: {group_id}
    
    Please add me to your group.
    """
    group_admin_email = crud.get_group_admin_email(group_id)
    twillio_response = send_email("New Signup Request", email_body, group_admin_email)
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
    db: Session = Depends(get_db),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    default_group = crud.get_default_group(db, current_user.id)
    challenge = crud.get_challenge_by_id(db, default_group.challenge_id)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user_id": current_user.id,
            "year": CURRENT_YEAR,
            "group_id": default_group.id,
            "group_name": default_group.name,
            "challenge_name": challenge.name,
        },
    )


@router.get("/all_users")
async def all_users(
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
    year: Optional[int] = Query(settings.CURRENT_YEAR),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    group = crud.get_default_group(db, current_user.id)
    return generate_leaderboard(db, group.id, year)


@router.get("/latest_submissions", response_class=JSONResponse)
def latest_submissions(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db: Session = Depends(get_db),
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    group = crud.get_default_group(db, current_user.id)
    latest_submissions = crud.get_latest_submissions(db, group.id)
    for submission in latest_submissions:
        user_name = crud.get_user(db, submission.user_id).username
        submission.__dict__["username"] = user_name
    return latest_submissions
