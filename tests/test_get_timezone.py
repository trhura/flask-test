from datetime import timedelta


def test_get_timezone_without_auth_token(client, usera):
    resp = client.get("/users/" + usera.uuid + "/timezones/3")
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_get_timezone_with_invalid_auth_token(client, userb, usera_auth_token):
    resp = client.get(
        "/users/" + userb.uuid + "/timezones/3",
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to get timezone of other users"


def test_get_timezone_with_invalid_id(client, usera, usera_auth_token):
    resp = client.get(
        "/users/" + usera.uuid + "/timezones/" + str(3),
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 404

    assert data["success"] is False
    assert data["message"] == "unable to find specified timezone"


def test_get_timezone_successful(client, usera, usera_auth_token, tza2):
    resp = client.get(
        "/users/" + usera.uuid + "/timezones/" + str(tza2.id),
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["timezone"]["user_id"] == usera.uuid
    assert data["timezone"]["name"] == tza2.name
    assert data["timezone"]["tzname"] == tza2.tzname
    assert data["timezone"]["utcoffset"] == str(timedelta(seconds=tza2.utcoffset))


def test_get_timezone_by_admin_successful(client, userb, admin_auth_token, tzb1):
    resp = client.get(
        "/users/" + userb.uuid + "/timezones/" + str(tzb1.id),
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["timezone"]["user_id"] == userb.uuid
    assert data["timezone"]["name"] == tzb1.name
    assert data["timezone"]["tzname"] == tzb1.tzname
    assert data["timezone"]["utcoffset"] == str(timedelta(seconds=tzb1.utcoffset))
