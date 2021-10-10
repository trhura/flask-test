def test_create_user_without_json_body(client):
    resp = client.post("/user")
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["success"] is False
    assert "Failed to decode JSON object" == data["message"]


def test_create_user_without_name_param(client):
    resp = client.post("/user", json={})
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["success"] is False
    assert "'name' is a required property" == data["message"]


def test_create_user_without_password_param(client):
    resp = client.post("/user", json={"name": "thura"})
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["success"] is False
    assert "'password' is a required property" == data["message"]


def test_create_user_with_invalid_name(client):
    resp = client.post("/user", json={"name": 3, "password": "asdf"})
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_user_with_invalid_password(client):
    resp = client.post("/user", json={"name": "thura", "password": 3})
    data = resp.get_json()
    assert resp.status_code == 400
    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_user_successful(client):
    resp = client.post("/user", json={"name": "thura", "password": "thura"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert data["success"] is True
    assert "new user created" == data["message"]


def test_list_users(client):
    assert 0 == 0


def test_delete_users(client):
    assert 0 == 0
