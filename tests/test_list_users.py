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
