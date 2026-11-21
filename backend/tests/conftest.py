import os

os.environ['DATABASE_URL'] = 'sqlite://'
os.environ["SECRET_KEY"] = "test-secret-key-that-is-at-least-32-bytes-long"
os.environ["R2_ENDPOINT_URL"] = "https://test.r2.cloudflarestorage.com"
os.environ["R2_ACCESS_KEY"] = "test-access-key"
os.environ["R2_SECRET_ACCESS_KEY"] = "test-secret"
os.environ["R2_BUCKET"] = "test-bucket"



import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import get_db
from app.main import app
from app.models import User

@pytest.fixture
def client(): 
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    User.__table__.create(engine)
    TestSession = sessionmaker(bind=engine, autoflush=False)

    def override_get_db():
        db = TestSession()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear
    engine.dispose()

@pytest.fixture
def registered_user(client):
    payload = {"username": "jonas", "password": "testpassword123"}
    client.post("/auth/register", json=payload)
    return payload
