from contextlib import asynccontextmanager

import models.models as models
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import engine, get_db
from fastapi import Depends, FastAPI
from fastapi.staticfiles import StaticFiles
from requests import Session
from routers import ai_recommendations, auth, bookmarks, categories, home, my_challenge, previous_challenges, profile
from utils.email import send_monthly_newsletter

models.Base.metadata.create_all(bind=engine)


jobstores = {"default": MemoryJobStore()}
scheduler = AsyncIOScheduler(jobstores=jobstores, timezone="Europe/Berlin")


@scheduler.scheduled_job("cron", month="1-12", day=15, hour=10, minute=0)
def newsletter_scheduler(db: Session = Depends(get_db)):
    send_monthly_newsletter(db)


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

app.mount("/static", StaticFiles(directory="static"), name="static")
