from datetime import datetime, timezone
from typing import List

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column, relationship

Base = declarative_base()


class GroupMembership(Base):
    __tablename__ = "group_membership"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("group.id"), primary_key=True)
    joined_at: Mapped[str] = mapped_column(String)

    user: Mapped["User"] = relationship(back_populates="group_memberships")
    group: Mapped["Group"] = relationship(back_populates="members")


class Association(Base):
    __tablename__ = "association_table"

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"), primary_key=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("challenge_category.id"), primary_key=True)
    book_name: Mapped[str] = mapped_column(String, unique=True)
    author: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=timezone.utc), index=True)
    challenge_category: Mapped["ChallengeCategory"] = relationship(back_populates="users")
    user: Mapped["User"] = relationship(back_populates="challenge_categories")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=timezone.utc))
    newsletter_email_address: Mapped[str] = mapped_column(String, nullable=True)
    group_memberships: Mapped[List["GroupMembership"]] = relationship(back_populates="user")
    challenge_categories: Mapped[List["Association"]] = relationship(back_populates="user")


class BookmarkedRecommendations(Base):
    __tablename__ = "bookmarked_recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=timezone.utc))
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    category_id: Mapped[int] = mapped_column(ForeignKey("challenge_category.id"))
    book_info: Mapped[str] = mapped_column(String)


class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    members: Mapped[List["GroupMembership"]] = relationship(back_populates="group")


class ChallengeCategory(Base):
    __tablename__ = "challenge_category"

    id: Mapped[int] = mapped_column(primary_key=True)
    original_number: Mapped[int] = mapped_column(Integer)
    title: Mapped[str] = mapped_column(String, index=True, unique=True)
    year: Mapped[int] = mapped_column(Integer, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=timezone.utc))
    user_id_custom_category: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    advanced: Mapped[bool] = mapped_column(Boolean, default=False)

    users: Mapped[List["Association"]] = relationship(back_populates="challenge_category")


class AllowedEmailAddress(Base):
    __tablename__ = "allowed_email_address"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(tz=timezone.utc))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
