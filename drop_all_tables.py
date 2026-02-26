from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from config import settings


if __name__ == '__main__':
    engine = create_engine(settings.database_url)

    Base = declarative_base()
    Base.metadata.reflect(bind=engine)
    Base.metadata.drop_all(bind=engine)

    engine.dispose()
