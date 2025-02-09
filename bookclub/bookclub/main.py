from contextlib import asynccontextmanager
from datetime import datetime, timedelta

import models.models as models
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import engine, get_db
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from models.models import TrophyType
from requests import Session
from routers import (
    ai_recommendations,
    auth,
    bookmarks,
    categories,
    home,
    my_challenge,
    previous_challenges,
    profile,
    statistics,
)
from utils.email import send_monthly_newsletter
from utils.trophy import TrophyService

models.Base.metadata.create_all(bind=engine)


jobstores = {"default": MemoryJobStore()}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Europe/Berlin")


@scheduler.scheduled_job("cron", month="1-12", day=15, hour=9, minute=5)
def newsletter_scheduler():
    send_monthly_newsletter()


@scheduler.scheduled_job("cron", month="1-12", day=1, hour=5, minute=0)
def monthly_trophy_calculator_scheduler():
    yesterday = datetime.now().replace(day=1) - timedelta(days=1)
    TrophyService(TrophyType.MONTHLY, "static/images/").calculate_trophy_monthly(1, yesterday.year)


@scheduler.scheduled_job("cron", month="1", day=1, hour=00, minute=1)
def yearly_trophy_calculator_scheduler():
    # todo we need the top 3 users of the year
    year = datetime.now().year - 1
    TrophyService(TrophyType.YEARLY, "static/images/").calculate_trophy_yearly(1, year)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(home.router)
app.include_router(ai_recommendations.router)
app.include_router(auth.router)
app.include_router(my_challenge.router)
app.include_router(bookmarks.router)
app.include_router(categories.router)
app.include_router(previous_challenges.router)
app.include_router(profile.router)
app.include_router(statistics.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(ai_recommendations.router)
app.include_router(auth.router)
app.include_router(my_challenge.router)
app.include_router(bookmarks.router)
app.include_router(categories.router)
app.include_router(previous_challenges.router)
app.include_router(profile.router)
app.include_router(statistics.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
