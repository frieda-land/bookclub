from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import JSONResponse, RedirectResponse
from models import models
from pydantic import EmailStr
from schemas.schema import GroupInvite, InvitedEmailCreate
from settings import settings
from utils.auth import get_current_active_user
from utils.email import inform_user_about_invitation, inform_user_about_signup
from utils.exceptions import UserInviteException

router = APIRouter(prefix="/group", tags=["group"])

CURRENT_YEAR = settings.CURRENT_YEAR


@router.get("/")
def group(
    request: Request, current_user: Annotated[models.User, Depends(get_current_active_user)], db=Depends(get_db)
) -> JSONResponse:
    if isinstance(current_user, RedirectResponse):
        return current_user
    user_groups = crud.get_groups_and_default_for_user(db, current_user.id)
    return user_groups


@router.get("/select")
def select_group(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db=Depends(get_db),
    group_name: str = Query(...),
) -> JSONResponse:
    if isinstance(current_user, RedirectResponse):
        return current_user
    group = crud.get_group_by_name(db, group_name)
    crud.update_group_membership_default(db, group.id, current_user.id, True)
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user_id": current_user.id,
            "year": CURRENT_YEAR,
            "group_id": group.id,
            "group_name": group.name,
            "challenge_name": crud.get_challenge_by_id(db, group.challenge_id).name,
        },
    )


@router.get("/my")
def my_groups(
    current_user: Annotated[models.User, Depends(get_current_active_user)], db=Depends(get_db)
) -> JSONResponse:
    if isinstance(current_user, RedirectResponse):
        return current_user
    admin_groups = crud.get_admin_groups_and_members(db, current_user.id)
    return admin_groups


@router.delete("/{group}/user/{email}")
def remove_user_from_group(
    group: str,
    email: str,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db=Depends(get_db),
) -> JSONResponse:
    if isinstance(current_user, RedirectResponse):
        return current_user
    try:
        breakpoint()
        group = crud.get_group_by_name(db, group)
        user = crud.get_user_by_email(db, email)
        crud.remove_user_from_group(db, group.id, user.id)
    except Exception:
        return JSONResponse(content={"message": "Failed to remove user from group."}, status_code=400)
    return JSONResponse(status_code=204, content="User removed from group.")


@router.delete("/{group}/invite/{email}")
def remove_allowed_email_for_group(
    group: str,
    email: str,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db=Depends(get_db),
) -> JSONResponse:
    if isinstance(current_user, RedirectResponse):
        return current_user
    try:
        group = crud.get_group_by_name(db, group)
        crud.remove_invited_allowed_email_for_group(db, group.id, email)
    except Exception:
        return JSONResponse(content={"message": "Failed to remove email from allowed emails."}, status_code=400)
    return JSONResponse(content={"message": "Email removed from allowed emails."})


@router.post("/add_user")
def add_user_to_group(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
    db=Depends(get_db),
    group: str = Form(...),
    email: EmailStr = Form(...),
) -> JSONResponse:
    if isinstance(current_user, RedirectResponse):
        return current_user

    group = crud.get_group_by_name(db, group)
    try:
        crud.create_invited_email(db, InvitedEmailCreate(email=email, is_invited_request_for_group_id=group.id))
        challenge_name = crud.get_challenge_by_id(db, group.challenge_id).name
        group_invite = GroupInvite(name=group.name, challenge_name=challenge_name)
        inform_user_about_invitation(email, current_user.username, group_invite)
    except UserInviteException:
        return templates.TemplateResponse(
            "admin.html",
            {
                "request": request,
                "content": {"message": "Sending invite email to user failed, we try sending it later."},
            },
            status_code=400,
        )
    except Exception:
        return templates.TemplateResponse(
            "admin.html",
            {"request": request, "content": {"message": "Failed to add user to group."}},
            status_code=400,
        )
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "content": {"message": "User added to group."}},
    )
