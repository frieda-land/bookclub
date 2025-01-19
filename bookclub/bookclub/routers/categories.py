from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from schemas.schema import ChallengeCategoryCreate, CreateAllCategoriesResponse
from utils.categories import advanced_challenges, challenges, create_single_category

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("/create")
def create_category(category: ChallengeCategoryCreate, db: Session = Depends(get_db), user_id: int = None):
    return create_single_category(db, category, user_id)


@router.post(
    "/create_all/{advanced}",
    response_model=CreateAllCategoriesResponse,
)
def create_all_categories(db: Session = Depends(get_db), advanced: bool = False):
    challenge = advanced_challenges if advanced else challenges
    created_categories = []
    try:
        for key, value in challenge.items():
            for category_id, title in value.items():
                category = ChallengeCategoryCreate(
                    original_number=category_id,
                    title=title,
                    year=key,
                    advanced=advanced,
                )
                try:
                    created_category = create_category(category, db)
                    created_categories.append(created_category)
                except HTTPException:
                    continue
    except Exception as e:
        # TODO add/use logging
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
