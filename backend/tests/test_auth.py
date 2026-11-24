from datetime import datetime, timedelta, timezone
import jwt
import os


def test_register_and_login(client):
    r = client.post(
        "/auth/register", json={"username": "test", "password": "testpassword123"}
    )
    assert r.status_code == 201
    assert r.json()["username"] == "test"
    assert "password_hash" not in r.json()

    r = client.post(
        "/auth/login", json={"username": "test", "password": "testpassword123"}
    )
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_register_duplicate_username(client, registered_user):
    second = client.post("/auth/register", json=registered_user)
    assert second.status_code == 409


def test_login_wrong_password(client, registered_user):
    r = client.post(
        "/auth/login",
        json={"username": registered_user["username"], "password": "wrongpassword123"},
    )
    assert r.status_code == 401


def test_login_no_user(client):
    r = client.post(
        "/auth/login", json={"username": "test", "password": "testpassword123"}
    )
    assert r.status_code == 401


def test_length_password(client):
    r = client.post("/auth/register", json={"username": "test", "password": "short"})
    assert r.status_code == 422

    r = client.post("/auth/register", json={"username": "test", "password": "a" * 73})
    assert r.status_code == 422

    r = client.post("/auth/register", json={"username": "test", "password": "é" * 40})
    assert r.status_code == 422


def test_length_username(client):
    r = client.post(
        "/auth/register", json={"username": "t", "password": "testpassword123"}
    )
    assert r.status_code == 422

    r = client.post(
        "/auth/register", json={"username": "a" * 31, "password": "testpassword123"}
    )
    assert r.status_code == 422


def test_username_strip(client):
    client.post(
        "/auth/register", json={"username": "  alice  ", "password": "testpassword123"}
    )

    r = client.post(
        "/auth/login", json={"username": "alice", "password": "testpassword123"}
    )
    assert r.status_code == 200

    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    body = client.get("/auth/me", headers=headers).json()
    assert body["username"] == "alice"


def test_me_valid_token(client, make_user):
    alice = make_user("alice")
    bob = make_user("bob")

    r = client.get("/auth/me", headers=alice)
    body = r.json()

    assert r.status_code == 200
    assert body["username"] == "alice"
    assert "id" in body
    assert "password_hash" not in body
    assert "password" not in body


def test_me_expired_token(client):
    token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=5)},
        "test-secret-key-that-is-at-least-32-bytes-long",  # same as SECRET_KEY in conftest
        algorithm="HS256",
    )
    r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 401
