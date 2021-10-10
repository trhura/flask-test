from models import User
from werkzeug.security import check_password_hash


def test_update_user_without_json_body(client, usera):
    resp = client.post("/users/" + usera.uuid)
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "Failed to decode JSON object"


def test_update_user_without_any_param(client, usera):
    resp = client.post("/users/" + usera.uuid, json={})
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "is a required property" in data["message"]


def test_update_user_without_auth_token(client, usera):
    resp = client.post("/users/" + usera.uuid, json={"fullname": "Thura"})
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_update_user_with_invalid_token(client, usera, userb_auth_token):
    resp = client.post(
        "/users/" + usera.uuid,
        json={"fullname": "Thura"},
        headers={
            "Authorization": "Bearer " + userb_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to update other users"


def test_update_user_succesful_fullname(client, usera, usera_auth_token):
    resp = client.post(
        "/users/" + usera.uuid,
        json={"fullname": "Thura"},
        headers={
            "Authorization": "Bearer " + usera_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "user updated successfully"

    user = User.query.filter_by(username=usera.username).first()
    assert user.fullname == "Thura"


def test_update_user_succesful_password(client, usera, usera_auth_token):
    resp = client.post(
        "/users/" + usera.uuid,
        json={"password": "newpass"},
        headers={
            "Authorization": "Bearer " + usera_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "user updated successfully"

    user = User.query.filter_by(username=usera.username).first()
    assert check_password_hash(user.password, "newpass") is True


def test_update_user_failed_admin(client, usera, usera_auth_token):
    resp = client.post(
        "/users/" + usera.uuid,
        json={"admin": True},
        headers={
            "Authorization": "Bearer " + usera_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "only admin can update admin users"


def test_update_user_succesful_admin(client, usera, admin_auth_token):
    resp = client.post(
        "/users/" + usera.uuid,
        json={"password": "xxx", "fullname": "newname", "admin": True},
        headers={
            "Authorization": "Bearer " + admin_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "user updated successfully"

    user = User.query.filter_by(username=usera.username).first()
    assert user.fullname == "newname"
    assert check_password_hash(user.password, "xxx") is True
    assert user.admin is True
