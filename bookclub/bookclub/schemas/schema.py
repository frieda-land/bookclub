from datetime import datetime
from typing import List

from pydantic import BaseModel


class ChallengeCategoryBase(BaseModel):
    title: str
    user_id_custom_category: int | None = None
    original_number: int | None = None
    year: int = 2025
    advanced: bool = False


class ChallengeCategoryCreate(ChallengeCategoryBase):
    pass


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


class User(UserBase):
    id: int
    created_at: datetime
    is_active: bool = True
    challenge_categories: List[ChallengeCategory] = []
    groups: List["Group"] = []


class NewsletterUser(BaseModel):
    newsletter_email_address: str
    username: str


class GroupBase(BaseModel):
    name: str
    description: str
    created_at: datetime


class GroupCreate(GroupBase):
    pass


class Group(GroupBase):
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


class CreateAllCategoriesResponse(BaseModel):
    status: str
    number_of_categories: int
    created_categories: List[ChallengeCategory]


class SubmittedBookWithUsername(SubmittedBook):
    username: str
    created_at: datetime
    category_id: int
