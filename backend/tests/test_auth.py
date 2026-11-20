
def test_register_and_login(client):
    r = client.post("/auth/register", json={"username": "jonas", "password": "testpassword123"})
    assert r.status_code == 201
    assert r.json()["username"] == "jonas"
    assert "password_hash" not in r.json()

    r = client.post("/auth/login", json={"username": "jonas", "password": "testpassword123"})
    assert r.status_code == 200
    assert "access_token" in r.json()