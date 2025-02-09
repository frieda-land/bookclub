from crud import crud
from database import engine
from models.models import TrophyType
from schemas import schema
from sqlalchemy.orm import sessionmaker


class TrophyService:
    def __init__(self, kind: TrophyType, image_path: str):
        self.kind = kind
        self.image_path = image_path

    def calculate_trophy_monthly(self, month: int, year: int):
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        reader_of_the_month = crud.get_reader_of_the_month(month, year, db)
        for reader in reader_of_the_month:
            trophy = schema.TrophyCreate(
                kind=self.kind,
                month=month,
                user_id=reader.user_id,
                number_of_books_read=reader.number_of_books_read,
                year=year,
            )
            crud.create_trophy(db, trophy)
            print(f"Created monthly trophy for user {reader.user_id} successfully")

    def calculate_trophy_yearly(self, year: int):
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        reader_of_the_year = crud.get_reader_of_the_year(year, db)
        for reader in reader_of_the_year:
            trophy = schema.TrophyCreate(
                kind=self.kind,
                month=None,
                user_id=reader.user_id,
                number_of_books_read=reader.number_of_books_read,
                year=year,
            )
            crud.create_trophy(db, trophy)
            print(f"Created yearly trophy for user {reader.user_id} successfully")
