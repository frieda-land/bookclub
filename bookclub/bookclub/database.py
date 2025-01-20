import pg8000
from google.cloud.sql.connector import Connector, IPTypes
from settings import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, pool_size=10, max_overflow=20
# )

Base = declarative_base()

db_user = settings.DB_USER  # e.g. 'my-db-user'
db_pass = settings.DB_PASS  # e.g. 'my-db-password'
db_name = settings.DB_NAME  # e.g. 'my-database'


# initialize Cloud SQL Python Connector object
connector = Connector()


def getconn() -> pg8000.dbapi.Connection:
    conn: pg8000.dbapi.Connection = connector.connect(
        settings.DATABASE_URL,
        "pg8000",
        user=db_user,
        password=db_pass,
        db=db_name,
        ip_type=IPTypes.PUBLIC,
    )
    return conn


# The Cloud SQL Python Connector can be used with SQLAlchemy
# using the 'creator' argument to 'create_engine'
engine = create_engine(
    "postgresql+pg8000://",
    creator=getconn,
    # ...
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        db.close()
