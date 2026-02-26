from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config import settings


# Database setup.
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Gets DB instance.
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


get_db()

SessionDep = Annotated[Session, Depends(get_db)]
