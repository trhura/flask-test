from base64 import b64encode


def test_user_login_without_auth_header(client):
    resp = client.post("/login")
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "Failed to authenticate user"


def test_user_login_with_invalid_credentials(client, usera):
    auth = b64encode(b"usera:wrongpass").decode("ascii")
    resp = client.post("/login", headers={"Authorization": "Basic " + auth})
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "Failed to authenticate user"


def test_user_login_with_invalid_user(client):
    auth = b64encode(b"usera:passa").decode("ascii")
    resp = client.post("/login", headers={"Authorization": "Basic " + auth})
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "Failed to authenticate user"


def test_user_login_successful(client, usera):
    auth = b64encode(b"usera:passa").decode("ascii")
    resp = client.post("/login", headers={"Authorization": "Basic " + auth})
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["auth_token"] is not None
    assert data["user"]["username"] == usera.username
    assert data["user"]["uuid"] == usera.uuid
