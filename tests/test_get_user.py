def test_get_user_without_auth_token(client, usera):
    resp = client.get("/user/" + usera.uuid)
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_get_user_with_invalid_id(client, usera, usera_auth_token):
    resp = client.get(
        "/user/" + "no-such-user",
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to access other users"


def test_get_user_with_invalid_auth_token(client, userb, usera_auth_token):
    resp = client.get(
        "/user/" + userb.uuid,
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to access other users"


def test_get_usera_successful(client, usera, usera_auth_token):
    resp = client.get(
        "/user/" + usera.uuid,
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["user"]["fullname"] == usera.fullname
    assert data["user"]["username"] == usera.username
    assert data["user"]["admin"] is False


def test_get_usera_by_admin_successful(client, usera, admin_auth_token):
    resp = client.get(
        "/user/" + usera.uuid,
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["user"]["fullname"] == usera.fullname
    assert data["user"]["username"] == usera.username
    assert data["user"]["admin"] is False
