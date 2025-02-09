import locale
from datetime import datetime

from crud import crud
from database import engine
from jinja2 import Environment, FileSystemLoader
from schemas.schema import NewsletterUser
from sendgrid import Mail, SendGridAPIClient
from settings import settings
from sqlalchemy.orm import sessionmaker
from utils.leaderboard import generate_leaderboard

EMAIL_ADMIN = settings.EMAIL_ADMIN
TWILLIO_KEY = settings.TWILLIO_KEY


# Todo create proper Email service
def send_monthly_newsletter():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        subscribers = crud.get_newsletter_subscribers(db)
        email_addresses = [
            NewsletterUser(
                newsletter_email_address=subscriber.newsletter_email_address,
                username=subscriber.username,
                user_id=subscriber.id,
            )
            for subscriber in subscribers
        ]
        leaderboard = generate_leaderboard(db)
        books_last_30_days = crud.get_last_submitted_books(db)
        readers_of_the_month = crud.get_reader_of_last_30_days(db)
        for email in email_addresses:
            locale.setlocale(locale.LC_TIME, "de_DE.UTF-8")
            context = {
                "recipient_name": email.username,
                "month": datetime.now().strftime("%B"),
                "leaderboard": leaderboard[:7],
                "unsubscribe_url": f"https://shelfie.frieda.dev/auth/unsubscribe/{email.user_id}",
                "number_of_books_read_last_30_days": len(books_last_30_days),
                "average_rating_last_30_days": round(
                    sum([book.rating for book in books_last_30_days]) / len(books_last_30_days), 2
                ),
                "readers_of_the_month": [
                    {"user": reader.user, "number_of_books_read": reader.number_of_books_read}
                    for reader in readers_of_the_month
                ],
            }
            locale.setlocale(locale.LC_TIME, "C")
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("newsletter.html", context)
            html = template.render(context)
            send_email("Monthly Newsletter", html, email.newsletter_email_address)
    finally:
        db.close()


def send_welcome_to_newsletter(db, recipient: NewsletterUser):
    try:
        context = {
            "recipient_name": recipient.username,
            "unsubscribe_url": f"https://shelfie.frieda.dev/auth/unsubscribe/{recipient.user_id}",
        }
        env = Environment(loader=FileSystemLoader("templates"))
        template = env.get_template("newsletter_welcome.html", context)
        html = template.render(context)
        send_email("Welcome To Monthly Newsletter", html, recipient.newsletter_email_address)
    finally:
        db.close()


def inform_user_about_signup(email: str):
    context = {
        "login_url": "https://shelfie.frieda.dev/login",
    }
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("welcome.html", context)
    html = template.render(context)
    try:
        send_email("Welcome to BookClub", html, email)
    except Exception:
        # todo add exponential backoff
        return


def send_email(subject: str, body: str, to: str = EMAIL_ADMIN):
    message = Mail(
        from_email=EMAIL_ADMIN,
        to_emails=to,
        subject=subject,
        html_content=body,
    )
    try:
        sg = SendGridAPIClient(TWILLIO_KEY)
        return sg.send(message)
    except Exception as e:
        raise e
