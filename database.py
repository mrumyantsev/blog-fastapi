
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config import settings


# Database setup.
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Gets DB instance.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


get_db()
