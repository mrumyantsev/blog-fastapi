from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db


# Setup the TestClient
client = TestClient(app)


# Setup the in-memory SQLite database for testing
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Dependency to override the get_db dependency in the main app
def override_get_db():
    database = TestingSessionLocal()
    yield database
    database.close()


app.dependency_overrides[get_db] = override_get_db


def test_register_user():
    response = client.post(
        '/api/register', json={'username': 'a', 'password': 'a', 'email': 'a@mail.com'}
    )
    assert response.status_code == 200
    assert response.json() == {'id': 1}
