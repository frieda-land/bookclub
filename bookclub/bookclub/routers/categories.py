from crud.crud import get_challenge_by_id
from database import get_db
from fastapi import APIRouter, Depends
from requests import Session
from schemas.schema import ChallengeCategoryCreate, CreateAllCategoriesResponse
from utils.categories import advanced_challenges, challenges, create_single_category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/create")
def create_category(category: ChallengeCategoryCreate, db: Session = Depends(get_db), user_id: int = None):
    return create_single_category(db, category, user_id)


@router.post(
    "/create_all",
    response_model=CreateAllCategoriesResponse,
)
def create_all_categories(
    challenge_id: int,
    advanced: bool = False,
    db: Session = Depends(get_db),
):
    challenge_kind = advanced_challenges if advanced else challenges
    challenge = get_challenge_by_id(db, challenge_id)
    year = None
    if challenge:
        year = challenge.year
    else:
        return {
            "status": f"No challenge with id {challenge_id}. Create a challenge first.",
            "created_categories": 0,
            "number_of_categories": 0,
        }
    created_categories = []
    try:
        for category_id, title in challenge_kind[year].items():
            category = ChallengeCategoryCreate(
                original_number=category_id,
                title=title,
                year=year,
                advanced=advanced,
                challenge_id=challenge_id,
            )
            created_category = create_category(category, db)
            created_categories.append(created_category)
    except Exception as e:
        print(e)
        return {
            "status": "Failed",
            "created_categories": created_categories,
            "number_of_categories": len(created_categories),
        }
    return {
        "status": "Success",
        "created_categories": created_categories,
        "number_of_categories": len(created_categories),
    }
