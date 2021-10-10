from models import User


def test_delete_user_without_auth_token(client, usera):
    resp = client.delete("/users/" + usera.uuid)
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_delete_user_without_admin_auth_token(client, usera, usera_auth_token):
    resp = client.delete(
        "/users/" + usera.uuid,
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "only admin user can access this route"


def test_delete_user_successful(client, randname, admin_auth_token):
    resp = client.post(
        "/users",
        json={"username": randname, "fullname": randname, "password": "pass"},
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    assert resp.status_code == 200

    user = User.query.filter_by(username=randname).first()
    assert user.username == randname

    resp = client.delete(
        "/users/" + user.uuid,
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "the user has been deleted"

    user = User.query.filter_by(username=randname).first()
    assert user is None
