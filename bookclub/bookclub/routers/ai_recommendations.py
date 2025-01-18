from typing import Annotated

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import JSONResponse, RedirectResponse, StreamingResponse
from models import models
from openai import AsyncOpenAI
from requests import Session
from settings import settings
from utils.auth import get_current_active_user

OPENAI_API_KEY = settings.OPENAI_API_KEY

router = APIRouter(prefix="/recommendations", tags=["recommendations"])
open_ai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def generate_recommendations_for_category(title: str, original_language: str, additional_info: str = None):
    # add alerting when credit is low
    stream = await open_ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": f"Empfiehl 10 Bücher für die Popsugar Reading Challenge 2025 in der Kategorie {title}. \
                Die Originalsprache sollte {original_language}.{additional_info}. Gib an, warum du diese Bücher empfiehlst.",
            }
        ],
        stream=True,
    )
    async for chunk in stream:
        yield chunk.choices[0].delta.content or ""


# use router for /recommendations
@router.get("/")
def get_recommendations(
    request: Request,
    current_user: Annotated[models.User, Depends(get_current_active_user)],
):
    if isinstance(current_user, RedirectResponse):
        return current_user
    return templates.TemplateResponse(
        request=request,
        name="recommendations.html",
        context={"user_id": current_user.id},
    )


@router.post("/")
async def post_recommendations(
    category: str = Form(...),
    original_language: str = Form(...),
    additional_info: str = Form(None),
):
    async def recommendation_generator():
        async for recommendation in generate_recommendations_for_category(category, original_language, additional_info):
            yield recommendation

    return StreamingResponse(recommendation_generator(), media_type="text/plain")


@router.post("/save_favourite")
async def save_recommendation(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    try:
        category_num = crud.get_category_by_original_number(db, data["category"]).id
        bookmark_content = data["content"].split(". ")[1]
        crud.add_bookmark(db, data["user_id"], category_num, bookmark_content)
    except KeyError:
        return JSONResponse(
            content={"message": "Failed to save favourite. Missing value"},
            status_code=400,
        )
    return {"message": "Favourite saved successfully"}


@router.post("/unsave_favourite")
async def unsave_recommendation(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    try:
        category_num = crud.get_category_by_original_number(db, data["category"])
        crud.remove_bookmark(data["user_id"], category_num)
    except KeyError:
        return JSONResponse(
            content={"message": "Failed to unsave favourite. Missing value"},
            status_code=400,
        )
    return {"message": "Favourite unsaved successfully"}
