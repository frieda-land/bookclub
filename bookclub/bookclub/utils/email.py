import os

from crud import crud
from jinja2 import Environment, FileSystemLoader
from schemas.schema import NewsletterUser
from sendgrid import Mail, SendGridAPIClient
from settings import settings

EMAIL_ADMIN = settings.EMAIL_ADMIN


def send_monthly_newsletter(db):
    try:
        subscribers = crud.get_newsletter_subscribers(db)
        email_addresses = [
            NewsletterUser(newsletter_email_address=subscriber.newsletter_email_address, username=subscriber.username)
            for subscriber in subscribers
        ]
        for email in email_addresses:
            context = {
                "recipient_name": email.username,
                "unsubscribe_url": "https://yourdomain.com/unsubscribe",
            }
            env = Environment(loader=FileSystemLoader("templates"))
            template = env.get_template("newsletter.html", context)
            html = template.render(context)
            send_email("Monthly Newsletter", html, email.newsletter_email_address)
    finally:
        db.close()


def send_email(subject: str, body: str, to: str = EMAIL_ADMIN):
    message = Mail(
        from_email=EMAIL_ADMIN,
        to_emails=to,
        subject=subject,
        html_content=body,
    )
    try:
        sg = SendGridAPIClient(os.getenv("TWILLIO_KEY"))
        return sg.send(message)
    except Exception as e:
        raise e
