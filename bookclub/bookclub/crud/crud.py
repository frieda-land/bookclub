import io
from datetime import datetime, timedelta
from typing import List

from fastapi import UploadFile
from google.cloud import storage
from models import models
from PIL import Image
from schemas import schema
from settings import settings
from sqlalchemy.orm import Session

CURRENT_YEAR = settings.CURRENT_YEAR
BUCKET_NAME = settings.GCLOUD_PICTURE_BUCKET


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email.lower()).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    db_user = models.User(email=user.email.lower(), username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ChallengeCategory).offset(skip).limit(limit).all()


def get_category_by_number(db: Session, original_number: int, year: int = 2025):
    return (
        db.query(models.ChallengeCategory)
        .filter(
            models.ChallengeCategory.id == original_number,
            models.ChallengeCategory.year == year,
        )
        .first()
    )


def get_latest_number_for_year(db: Session, year: int = 2025):
    try:
        largest_category = (
            db.query(models.ChallengeCategory)
            .filter(
                models.ChallengeCategory.year == year,
            )
            .order_by(models.ChallengeCategory.year)
            .all()
        )[-1]
        return largest_category.original_number
    except IndexError:
        return 0


def get_category_by_original_number(db: Session, original_number: int, year: int = 2025):
    return (
        db.query(models.ChallengeCategory)
        .filter(
            models.ChallengeCategory.original_number == original_number,
            models.ChallengeCategory.year == year,
        )
        .first()
    )


def get_category_by_title(db: Session, title: str, year: int = 2025):
    return (
        db.query(models.ChallengeCategory)
        .filter(
            models.ChallengeCategory.title == title,
            models.ChallengeCategory.year == year,
        )
        .first()
    )


def create_challenge_category(db: Session, item: schema.ChallengeCategoryCreate):
    db_item = models.ChallengeCategory(
        original_number=item.original_number,
        title=item.title,
        year=item.year,
        user_id_custom_category=item.user_id_custom_category,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_category_for_user(db: Session, user_id: int, category_id: int):
    return (
        db.query(models.Association)
        .filter(
            models.Association.category_id == category_id,
            models.Association.user_id == user_id,
        )
        .first()
    )


def create_entry_for_user(
    db: Session,
    user_id: int,
    original_number: int,
    year: int,
    submitted_book: schema.SubmittedBook,
):
    category_id = get_category_by_original_number(db, original_number, year).id
    existing_entry = get_category_for_user(db, user_id, category_id)
    if existing_entry:
        print("Already exists")
        return
    db_category = models.Association(
        user_id=user_id,
        category_id=category_id,
        book_name=submitted_book.name,
        author=submitted_book.author,
        rating=submitted_book.rating,
    )
    db.add(db_category)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    db.refresh(db_category)
    return db_category


def delete_entry_for_user(
    db: Session,
    user_id: int,
    category_number: int,
):
    category_id = get_category_by_original_number(db, category_number).id
    item = (
        db.query(models.Association)
        .filter(
            models.Association.user_id == user_id,
            models.Association.category_id == category_id,
        )
        .first()
    )
    db.delete(item)
    db.commit()


def get_books_for_user(db: Session, user_id: str):
    user = get_user(db, int(user_id))
    if not user:
        # handle
        pass
    return user.challenge_categories


def get_books_for_user_for_year(db: Session, user_id: str, year: int):
    user = get_user(db, int(user_id))
    return [challenge for challenge in user.challenge_categories if challenge.challenge_category.year == year]


def get_books_for_user_for_last_30_days(db: Session, user_id: int):
    checkpoint = datetime.now() - timedelta(days=30)
    return (
        db.query(models.Association)
        .filter(
            models.Association.user_id == user_id,
            models.Association.created_at > checkpoint,
        )
        .all()
    )


# todo make year dynamic
def get_unused_categories(db: Session, user_id: int, year: int):
    return (
        db.query(models.ChallengeCategory)
        .filter(
            ~models.ChallengeCategory.users.any(user_id=user_id),
            models.ChallengeCategory.year == year,
        )
        .all()
    )


def get_latest_submissions(db: Session, limit: int = 3):
    first_day_of_year = datetime(CURRENT_YEAR, 1, 1)
    return (
        db.query(models.Association)
        .join(models.ChallengeCategory, models.Association.category_id == models.ChallengeCategory.id)
        .filter(
            models.Association.created_at > first_day_of_year,
            models.ChallengeCategory.year == CURRENT_YEAR,
        )
        .order_by(models.Association.created_at.desc())
        .limit(limit)
        .all()
    )


def add_bookmark(db: Session, user_id: int, category_id: int, book_info: str):
    bookmark = models.BookmarkedRecommendations(
        user_id=user_id,
        category_id=category_id,
        book_info=book_info,
    )
    db.add(bookmark)
    db.commit()
    db.refresh(bookmark)
    return bookmark


def remove_bookmark(db: Session, user_id: int, category_id: int):
    bookmark = (
        db.query(models.BookmarkedRecommendations)
        .filter(
            models.BookmarkedRecommendations.user_id == user_id,
            models.BookmarkedRecommendations.category_id == category_id,
        )
        .first()
    )
    db.delete(bookmark)
    db.commit()


def get_favourites(db: Session, user_id: int):
    return db.query(models.BookmarkedRecommendations).filter(models.BookmarkedRecommendations.user_id == user_id).all()


def remove_bookmark_by_id(db: Session, bookmark_id: int):
    bookmark = (
        db.query(models.BookmarkedRecommendations)
        .filter(
            models.BookmarkedRecommendations.id == bookmark_id,
        )
        .first()
    )
    db.delete(bookmark)
    db.commit()


def get_custom_categories(db: Session, user_id: int, year: int = 2025):
    return (
        db.query(models.ChallengeCategory)
        .filter(
            models.ChallengeCategory.user_id_custom_category == user_id,
            models.ChallengeCategory.year == year,
        )
        .all()
    )


def remove_category_by_title(db: Session, title: str, user_id: int):
    category = (
        db.query(models.ChallengeCategory)
        .filter(
            models.ChallengeCategory.title == title,
            models.ChallengeCategory.user_id_custom_category == user_id,
        )
        .first()
    )
    db.delete(category)
    db.commit()
    return category


def submitted_books_for_category_by_title(db: Session, title: str):
    category_id = db.query(models.ChallengeCategory).filter(models.ChallengeCategory.title == title).first().id
    categories = (
        db.query(models.Association)
        .filter(
            models.Association.category_id == category_id,
        )
        .all()
    )
    return categories


def subscribe_user_to_newsletter(db: Session, user: models.User, email: str):
    user = get_user(db, user.id)
    user.newsletter_email_address = email.lower()
    db.commit()
    db.refresh(user)
    return user


def unsubscribe_user_from_newsletter(db: Session, user: models.User):
    user = get_user(db, user.id)
    user.newsletter_email_address = None
    db.commit()
    db.refresh(user)
    return user


def get_newsletter_subscribers(db: Session):
    return db.query(models.User).filter(models.User.newsletter_email_address.isnot(None)).all()


def create_allowed_email(db: Session, allowed_email: schema.AllowedEmailCreate):
    allowed_email = models.AllowedEmailAddress(email=allowed_email.email.lower())
    db.add(allowed_email)
    try:
        db.commit()
    except Exception:
        db.rollback()
        return
    db.refresh(allowed_email)
    return allowed_email


def is_allowed_email(db: Session, email: str):
    return db.query(models.AllowedEmailAddress).filter(models.AllowedEmailAddress.email == email.lower()).first()


def get_last_submitted_books(db: Session, time_delta: int = 30):
    checkpoint = datetime.now() - timedelta(days=time_delta)
    return db.query(models.Association).filter(models.Association.created_at > checkpoint).all()


def get_books_of_month(month: int, year: int, db: Session):
    return db.query(models.Association).filter(models.Association.created_at >= datetime(year, month, 1)).all()


def get_books_of_year(year: int, db: Session):
    return db.query(models.Association).filter(models.Association.created_at >= datetime(year, 1, 1)).all()


# todo reafactor into one method
def get_reader_of_the_month(month: int, year: int, db: Session) -> List[schema.TrophyReaderUserId | None]:
    all_readers_of_the_month = {}
    all_books_of_the_month = get_books_of_month(month, year, db)
    for book in all_books_of_the_month:
        if book.user_id not in all_readers_of_the_month:
            all_readers_of_the_month[book.user_id] = 1
        else:
            all_readers_of_the_month[book.user_id] += 1
    current_max = 0
    readers_of_the_month = []
    for user_id, books_read in all_readers_of_the_month.items():
        if books_read > current_max:
            readers_of_the_month = []
            readers_of_the_month.append(schema.TrophyReaderUserId(user_id=user_id, number_of_books_read=books_read))
            current_max = books_read
        elif books_read == current_max:
            readers_of_the_month.append(schema.TrophyReaderUserId(user_id=user_id, number_of_books_read=books_read))
    return readers_of_the_month


def get_reader_of_the_year(year: int, db: Session) -> List[schema.TrophyReaderUserId | None]:
    all_readers_of_the_month = {}
    all_books_of_the_month = get_books_of_year(year, db)
    for book in all_books_of_the_month:
        if book.user_id not in all_readers_of_the_month:
            all_readers_of_the_month[book.user_id] = 1
        else:
            all_readers_of_the_month[book.user_id] += 1
    current_max = 0
    readers_of_the_month = []
    for user_id, books_read in all_readers_of_the_month.items():
        if books_read > current_max:
            readers_of_the_month = []
            readers_of_the_month.append(schema.TrophyReaderUserId(user_id=user_id, number_of_books_read=books_read))
            current_max = books_read
        elif books_read == current_max:
            readers_of_the_month.append(schema.TrophyReaderUserId(user_id=user_id, number_of_books_read=books_read))
    return readers_of_the_month


def get_reader_of_last_30_days(db: Session):
    all_readers_of_the_month = []
    current_max = 0
    for user in get_users(db):
        users_completed_categories = get_books_for_user_for_last_30_days(db, user.id)
        amount = len(users_completed_categories)
        if amount == 0:
            continue
        if amount > current_max:
            all_readers_of_the_month = []
            all_readers_of_the_month.append(schema.ReaderOfTheMonth(user=user.username, number_of_books_read=amount))
            current_max = len(users_completed_categories)
        elif amount == current_max:
            all_readers_of_the_month.append(schema.ReaderOfTheMonth(user=user.username, number_of_books_read=amount))
    return all_readers_of_the_month


month_names = [
    "Januar",
    "Februar",
    "März",
    "April",
    "Mai",
    "Juni",
    "Juli",
    "August",
    "September",
    "Oktober",
    "November",
    "Dezember",
]


def get_last_months(number_of_months: int):
    current_month = datetime.now().month
    current = current_month
    months = []
    while current > 0:
        months.append(current)
        current -= 1
    if len(months) != number_of_months:
        current = 12
        while len(months) < number_of_months:
            months.append(current)
            current -= 1
    month_buckets = {}
    months.reverse()
    for m in months:
        month_buckets[month_names[m - 1]] = 0
    return month_buckets


def fill_monthly_buckets(books: List[models.Association]):
    monthly_buckets = get_last_months(6)
    for book in books:
        month = month_names[book.created_at.month - 1]
        monthly_buckets[month] += 1
    return monthly_buckets


def get_statistics(db: Session):
    books_last_6_months = get_last_submitted_books(db, 180)
    monthly_buckets = fill_monthly_buckets(books_last_6_months)
    return {
        "months": list(monthly_buckets.keys()),
        "data": list(monthly_buckets.values()),
    }


def upload_bookcover(db: Session, file_wrapper: UploadFile, book_name: str, author: str):
    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)

    blob = bucket.blob(f"bookcovers/{book_name}-{author}.jpg")

    image = Image.open(file_wrapper.file)
    compressed_image_io = io.BytesIO()
    image.save(compressed_image_io, format="JPEG", quality=70)
    compressed_image_io.seek(0)

    blob.upload_from_file(compressed_image_io, content_type="image/jpeg")

    return blob.public_url


def create_trophy(db: Session, tropy: schema.TrophyCreate):
    db_trophy = models.Trophy(
        user_id=tropy.user_id,
        kind=tropy.kind,
        month=tropy.month,
        year=tropy.year,
        number_of_books_read=tropy.number_of_books_read,
    )
    db.add(db_trophy)
    db.commit()
    db.refresh(db_trophy)
    return db_trophy
