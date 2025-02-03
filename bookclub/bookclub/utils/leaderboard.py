from crud import crud
from settings import settings

CURRENT_YEAR = settings.CURRENT_YEAR


def generate_leaderboard(db, year=CURRENT_YEAR):
    all_users = []
    for user in crud.get_users(db):
        users_completed_categories = crud.get_books_for_user_for_year(db, user.id, year)
        # if len(users_completed_categories) == 0:
        #     continue
        all_users.append(
            {
                "number_of_books_read": len(users_completed_categories),
                "owner": user.username,
                "email": user.email,
                "books": [
                    {
                        "book_name": item.book_name,
                        "author": item.author,
                        "rating": item.rating,
                        "isbn": item.isbn,
                        "original_number": item.challenge_category.original_number,
                        "category_title": item.challenge_category.title,
                    }
                    for item in users_completed_categories
                ],
            }
        )
    return sorted(all_users, key=lambda item: item["number_of_books_read"], reverse=True)
