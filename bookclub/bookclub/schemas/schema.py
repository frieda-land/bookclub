from datetime import datetime
from typing import List

from models.models import TrophyType
from pydantic import BaseModel
from settings import settings


class ChallengeBase(BaseModel):
    name: str
    description: str
    year: int = settings.CURRENT_YEAR


class ChallengeCreate(ChallengeBase):
    pass


class ChallengeCategoryBase(BaseModel):
    title: str
    user_id_custom_category: int | None = None
    original_number: int | None = None
    year: int = 2025
    advanced: bool = False


class ChallengeCategoryCreate(ChallengeCategoryBase):
    group_id_custom_category: int | None = None
    challenge_id: int | None = None


class ChallengeCategory(ChallengeCategoryBase):
    id: int
    created_at: datetime
    users: List["User"] = []

    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    pass


class UserGroupUpdate(BaseModel):
    group_id: int
    user_id: int


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True
    challenge_categories: List[ChallengeCategory] = []
    groups: List["Group"] = []


class NewsletterUser(BaseModel):
    newsletter_email_address: str
    username: str
    user_id: int


class ReaderOfTheMonth(BaseModel):
    user: str
    number_of_books_read: int


class TrophyReaderUserId(BaseModel):
    user_id: int
    number_of_books_read: int


class GroupBase(BaseModel):
    name: str


class GroupInvite(GroupBase):
    challenge_name: str


class GroupCreate(GroupBase):
    description: str
    challenge_id: int
    admin_id: int | None = None


class Group(GroupCreate):
    id: int
    members: List[User] = []

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class SubmittedBook(BaseModel):
    author: str
    name: str
    rating: int
    group_id: int | None = None


class CreateAllCategoriesResponse(BaseModel):
    status: str
    number_of_categories: int
    created_categories: List[ChallengeCategory]


class SubmittedBookWithUsername(SubmittedBook):
    username: str
    created_at: datetime
    category_id: int


class AllowedEmailCreate(BaseModel):
    email: str
    is_admin_request_for_group_id: int | None = None
    is_user_request_for_group_id: int | None = None


class InvitedEmailCreate(BaseModel):
    email: str
    is_invited_request_for_group_id: int | None = None


class TrophyCreate(BaseModel):
    kind: TrophyType
    year: int
    number_of_books_read: int
    group_id: int | None = None
    user_id: int | None = None
    month: int | None = None
    month: int | None = None
