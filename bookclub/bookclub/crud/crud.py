from models import models
from schemas import schema
from sqlalchemy.orm import Session


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schema.UserCreate):
    db_user = models.User(email=user.email, username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_categories(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ChallengeCategory).offset(skip).limit(limit).all()


def get_category_by_number(db: Session, category_number: int, year: int = 2025):
    return (
        db.query(models.ChallengeCategory)
        .filter(
            models.ChallengeCategory.id == category_number,
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


def get_category_for_user(db: Session, user_id: int, category_number: int):
    category = get_category_by_number(db, category_number)
    if not category:
        # todo handle case
        pass
    exists = (
        db.query(models.Association)
        .filter(
            models.Association.category_id == category.id,
            models.Association.user_id == user_id,
        )
        .first()
    )
    return exists


def create_entry_for_user(
    db: Session,
    user_id: str,
    original_number: int,
    year: int,
    submitted_book: schema.SubmittedBook,
):
    category_id = get_category_by_original_number(db, original_number, year).id
    db_category = models.Association(
        user_id=user_id,
        category_id=category_id,
        book_name=submitted_book.name,
        author=submitted_book.author,
        rating=submitted_book.rating,
    )
    db.add(db_category)
    db.commit()
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
    if not user:
        # handle
        pass
    return [challenge for challenge in user.challenge_categories if challenge.challenge_category.year == year]


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
    return db.query(models.Association).order_by(models.Association.created_at.desc()).limit(limit).all()


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
    user.newsletter_email_address = email
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
    return db.query(models.User).filter(models.User.newsletter_email_address is not None).all()


def create_allowed_email(db: Session, allowed_email: schema.AllowedEmailCreate):
    allowed_email = models.AllowedEmailAddress(email=allowed_email.email)
    db.add(allowed_email)
    db.commit()
    db.refresh(allowed_email)
    return allowed_email
