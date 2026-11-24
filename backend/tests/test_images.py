import pytest

@pytest.mark.parametrize("method,url", [
    ("post", "/images/sign"),
    ("post", "/images/complete"),
    ("get", "/images"),
    ("delete", "/images/1"),
    ("get", "/images/search?query=dog"),
])
def test_requires_auth(client, method, url):
    assert getattr(client, method)(url).status_code == 401


def upload_image(client, headers, fake_storage, size=1000):
    r = client.post("/images/sign", headers=headers,
                    json={"content_type": "image/jpeg", "size": size})
    key = r.json()["storage_key"]
    fake_storage.objects[key] = size
    return client.post("/images/complete", headers=headers,
                       json={"storage_key": key})


def test_sign_returns_user_prefixed_key(client, make_user, fake_storage):
    headers = make_user()
    r = client.post("/images/sign", headers=headers,
                    json={"content_type": "image/jpeg", "size": 1000})
    assert r.status_code == 200
    body = r.json()
    assert body["upload_url"].startswith("https://fake/")
    assert body["storage_key"].endswith(".jpg")

def test_sign_unsupported_media(client, make_user, fake_storage):
    alice = make_user("alice")
    r = client.post("/images/sign",
                    headers=alice,
                    json={"content_type": "image/gif", "size": 1000})
    assert r.status_code == 415

def test_complete_other_users_key(client, make_user, fake_storage):
    alice = make_user("alice")
    bob = make_user("bob")

    alice_key = client.post("/images/sign", headers=alice, json={"content_type": "image/jpeg","size": 1000,}).json()["storage_key"]
    
    bob_key = client.post("/images/sign", headers=bob, json={"content_type": "image/jpeg","size": 1000,}).json()["storage_key"]
    fake_storage.objects[bob_key] = 1000   

    r = client.post("/images/complete", headers=alice, json={"storage_key": bob_key})
    assert r.status_code == 403
    assert fake_storage.deleted == []
    assert client.get("/images", headers=alice).json() == []

def test_gallery_only_shows_own_images(client, make_user, fake_storage):
    alice = make_user("alice")
    bob = make_user("bob")

    upload_image(client, alice, fake_storage)

    assert len(client.get("/images", headers=alice).json()) == 1
    assert client.get("/images", headers=bob).json() == []

def test_delete_other_users_img(client, make_user, fake_storage):
    alice = make_user("alice")
    bob = make_user("bob")

    image_id = upload_image(client, alice, fake_storage).json()["id"]
    r = client.delete(f"/{image_id}", headers=bob)
    assert r.status_code == 404
    assert len(client.get("/images",headers=alice).json()) == 1
