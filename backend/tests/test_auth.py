
def test_register_and_login(client):
    r = client.post("/auth/register", json={"username": "test", "password": "testpassword123"})
    assert r.status_code == 201
    assert r.json()["username"] == "test"
    assert "password_hash" not in r.json()

    r = client.post("/auth/login", json={"username": "test", "password": "testpassword123"})
    assert r.status_code == 200
    assert "access_token" in r.json()

def test_register_duplicate_username(client, registered_user):
    second = client.post("/auth/register", json=registered_user)
    assert second.status_code == 409

def test_login_wrong_password(client, registered_user):
    r = client.post(
        "/auth/login",
        json ={"username": registered_user["username"], "password": "wrongpassword123"}
    )
    assert r.status_code == 401