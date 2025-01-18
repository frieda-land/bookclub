import os
from datetime import datetime

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # generate your own secret key with the following command ssh-keygen -t rsa -b 4096 -m PEM
    SECRET_KEY: str = os.getenv("SECRET_KEY")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 2880  # 2 days
    AUTHORIZE_URL_GOOGLE: str = "https://accounts.google.com/o/oauth2/auth"
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET")
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/auth/google"
    GOOGLE_USER_INFO_URL: str = "https://www.googleapis.com/oauth2/v1/userinfo"
    ALLOWED_EMAILS: list[str] = []
    EMAIL_ADMIN: str = os.getenv("EMAIL_ADMIN")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    CURRENT_YEAR: int = datetime.now().year
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    TWILLIO_KEY: str = os.getenv("TWILLIO_KEY")

    class Config:
        env_file = ".env"


settings = Settings()
