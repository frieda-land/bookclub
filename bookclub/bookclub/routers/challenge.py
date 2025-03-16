from crud.crud import create_challenge, get_all_challenges
from database import get_db
from fastapi import APIRouter, Depends
from requests import Session
from schemas.schema import ChallengeCreate
from settings import settings

router = APIRouter(prefix="/challenge", tags=["challenge"])


@router.post("/create")
def create_new_challenge(name: str, description: str, year: int = settings.CURRENT_YEAR, db: Session = Depends(get_db)):
    challenge = ChallengeCreate(name=name, description=description, year=year)
    return create_challenge(db, challenge)


@router.get("/")
def get_challenges(db: Session = Depends(get_db)):
    return get_all_challenges(db)
