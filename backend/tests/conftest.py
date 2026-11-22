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

from app.database import Base, get_db
from app.main import app
from app import models

from sqlalchemy.ext.compiler import compiles
from pgvector.sqlalchemy import Vector

# add sqlite fix with vectors
@compiles(Vector, "sqlite")
def compile_vector_sqlite(element, compiler, **kw):
    return "TEXT"


@pytest.fixture
def client(): 
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    Base.metadata.create_all(engine)
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


@pytest.fixture
def make_user(client):
    def _make(username="testuser"):
        creds={"username": username, "password": "testpassword123"}
        client.post('/auth/register', json=creds)
        r = client.post('/auth/login', json=creds)
        return {"Authorization": f"Bearer {r.json()['access_token']}"}
    return _make


@pytest.fixture
def fake_storage(monkeypatch):
    objects = {} # key -> size
    deleted = []

    monkeypatch.setattr("app.routers.images.create_presigned_put",
                        lambda key, ct: f"https://fake/{key}")
    monkeypatch.setattr("app.routers.images.create_presigned_get",
                        lambda key: f"https://fake/{key}")
    monkeypatch.setattr("app.routers.images.object_size",
                        lambda key: objects.get(key))
    monkeypatch.setattr("app.routers.images.delete_object",
                        lambda key: deleted.append(key))
    class Fake:
        pass
    fake = Fake()
    fake.objects, fake.deleted = objects, deleted
    return fake

@pytest.fixture(autouse=True)
def fake_queue(monkeypatch):
    enqueued = []
    monkeypatch.setattr("app.routers.images.queue.enqueue",
                        lambda fn, *args, **kwargs: enqueued.append((fn, args)))
    return enqueued
