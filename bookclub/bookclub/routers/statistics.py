import json

from config import templates
from crud import crud
from database import get_db
from fastapi import APIRouter, Depends, Request

router = APIRouter(prefix="/statistics", tags=["statistics"])


@router.get("/")
def statistics(request: Request, db=Depends(get_db)):
    chart_data = crud.get_statistics(db)
    readers_of_the_month = crud.get_reader_of_last_30_days(db)
    return templates.TemplateResponse(
        "statistics.html",
        {
            "request": request,
            "chartData": json.dumps(chart_data),
            "readers_of_the_month": [reader.__dict__ for reader in readers_of_the_month],
        },
    )
