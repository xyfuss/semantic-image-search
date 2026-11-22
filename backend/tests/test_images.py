def upload_image(client, headers, fake_storage, size=1000):
    """Go through sign -> (fake) upload -> complete. Returns the /complete response."""
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


def test_gallery_only_shows_own_images(client, make_user, fake_storage):
    alice = make_user("alice")
    bob = make_user("bob")

    upload_image(client, alice, fake_storage)

    assert len(client.get("/images", headers=alice).json()) == 1
    assert client.get("/images", headers=bob).json() == []

