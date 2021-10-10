from datetime import timedelta


def test_list_timezones_without_auth_token(client, usera):
    resp = client.get("/users/" + usera.uuid + "/timezones")
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_list_timezones_with_invalid_auth_token(client, usera, tza1, userb_auth_token):
    resp = client.get(
        "/users/" + usera.uuid + "/timezones",
        headers={"Authorization": "Bearer " + userb_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to get timezone of other users"


def test_list_timezones_successful_empty(client, usera, usera_auth_token):
    resp = client.get(
        "/users/" + usera.uuid + "/timezones",
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["timezones"]) == 0


def test_list_timezones_successful(client, usera, usera_auth_token, tza1, tza2):
    resp = client.get(
        "/users/" + usera.uuid + "/timezones",
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["timezones"]) == 2


def test_list_timezones_successful_admin(client, userb, admin_auth_token, tzb1):
    resp = client.get(
        "/users/" + userb.uuid + "/timezones",
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["timezones"]) == 1
    assert data["timezones"][0]["user_id"] == userb.uuid
    assert data["timezones"][0]["name"] == tzb1.name
    assert data["timezones"][0]["tzname"] == tzb1.tzname
    assert data["timezones"][0]["utcoffset"] == str(timedelta(seconds=tzb1.utcoffset))
