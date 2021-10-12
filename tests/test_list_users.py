import uuid
from models import User, db


def test_list_users_without_auth_token(client):
    resp = client.get("/users")
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing" == data["message"]


def test_list_users_without_admin_auth_token(client, usera_auth_token):
    resp = client.get(
        "/users",
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "only admin user can access this route"


def test_list_users_with_usera(client, usera, admin_auth_token):
    resp = client.get(
        "/users",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["users"]) == 2

    assert "password" not in data["users"][0]
    assert "username" in data["users"][0]
    assert "fullname" in data["users"][0]
    assert "admin" in data["users"][0]


def test_list_users_with_usera_userb(client, usera, userb, admin_auth_token):
    resp = client.get(
        "/users",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["users"]) == 3


def test_list_users_with_pagination(client, admin_auth_token):
    for i in range(100):
        uid = str(uuid.uuid4())
        user = User(
            uuid=uid,
            fullname="Dummy user",
            username=uid,
            password="xxx",
        )
        db.session.add(user)

    db.session.commit()

    resp = client.get(
        "/users",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert len(data["users"]) == 20
    assert data["success"] is True
    assert data["prev_page"] is None
    assert data["current_page"] == 1
    assert data["next_page"] == 2
    assert data["per_page"] == 20
    assert data["total"] == 101  # with admin
    assert data["pages"] == 6

    resp = client.get(
        "/users?page=2",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert len(data["users"]) == 20
    assert data["success"] is True
    assert data["prev_page"] == 1
    assert data["current_page"] == 2
    assert data["next_page"] == 3
    assert data["per_page"] == 20
    assert data["total"] == 101  # with admin
    assert data["pages"] == 6

    resp = client.get(
        "/users?page=6",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert len(data["users"]) == 1
    assert data["success"] is True
    assert data["prev_page"] == 5
    assert data["current_page"] == 6
    assert data["next_page"] is None
    assert data["per_page"] == 20
    assert data["total"] == 101  # with admin
    assert data["pages"] == 6

    resp = client.get(
        "/users?page=2&per_page=25",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert len(data["users"]) == 25
    assert data["success"] is True
    assert data["prev_page"] == 1
    assert data["current_page"] == 2
    assert data["next_page"] == 3
    assert data["per_page"] == 25
    assert data["total"] == 101  # with admin
    assert data["pages"] == 5
