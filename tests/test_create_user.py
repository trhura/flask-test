from models import User

from werkzeug.security import check_password_hash


def test_create_user_without_json_body(client):
    resp = client.post("/users")
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "Failed to decode JSON object"


def test_create_user_without_name_param(client):
    resp = client.post("/users", json={})
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "'fullname' is a required property"


def test_create_user_without_password_param(client):
    resp = client.post("/users", json={"fullname": "Thura"})
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "'password' is a required property"


def test_create_user_without_username_param(client):
    resp = client.post(
        "/users",
        json={"fullname": "Thura", "password": "asdf"},
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "'username' is a required property"


def test_create_user_with_invalid_fullname(client):
    resp = client.post(
        "/users", json={"fullname": 3, "password": "asdf", "username": "thura"}
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_user_with_invalid_password(client):
    resp = client.post(
        "/users", json={"fullname": "Thura", "password": 3, "username": "thura"}
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_user_with_invalid_username(client):
    resp = client.post(
        "/users", json={"fullname": 3, "password": "asdf", "username": "thura"}
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_user_successful(client, randname):
    resp = client.post(
        "/users",
        json={"fullname": randname.upper(), "username": randname, "password": "asfd"},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "new user created"

    user = User.query.filter_by(username=randname).first()
    assert user.fullname == randname.upper()
    assert user.username == randname
    assert check_password_hash(user.password, "asfd") is True
    assert user.admin is False


def test_create_user_failed_on_duplicate(client, randname):
    resp = client.post(
        "/users",
        json={"fullname": randname.upper(), "username": randname, "password": "asfd"},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "new user created"

    resp = client.post(
        "/users",
        json={"fullname": randname.upper(), "username": randname, "password": "asfd"},
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "The username is already being used in the system"


def test_create_user_admin_without_auth_token(client):
    resp = client.post(
        "/users",
        json={
            "fullname": "user",
            "username": "user",
            "password": "pass",
            "admin": True,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "only admin can create admin users"


def test_create_user_admin_without_admin_auth_token(client, usera_auth_token):
    resp = client.post(
        "/users",
        json={
            "fullname": "thura",
            "username": "user",
            "password": "thura",
            "admin": True,
        },
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "only admin can create admin users"


def test_create_user_admin_successful(client, randname, admin_auth_token):
    resp = client.post(
        "/users",
        json={
            "fullname": randname.upper(),
            "username": randname,
            "password": "rootpass",
            "admin": True,
        },
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "new user created"

    user = User.query.filter_by(username=randname).first()
    assert user.username == randname
    assert user.fullname == randname.upper()
    assert check_password_hash(user.password, "rootpass") is True
    assert user.admin is True
