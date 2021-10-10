from models import Timezone


def test_create_timezone_without_json_body(client, usera):
    resp = client.post("/users/" + usera.uuid + "/timezones")
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "Failed to decode JSON object"


def test_create_timezone_without_name_param(client, usera):
    resp = client.post("/users/" + usera.uuid + "/timezones", json={})
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "'name' is a required property"


def test_create_timezone_without_tzname_param(client, usera):
    resp = client.post("/users/" + usera.uuid + "/timezones", json={"name": "Home"})
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "'tzname' is a required property"


def test_create_timezone_with_invalid_name(client, usera):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones", json={"name": 3, "tzname": "Asia/Yangon"}
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_timezone_with_invalid_tzname(client, usera):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": "Home", "tzname": 3},
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "not of type 'string'" in data["message"]


def test_create_timezone_without_auth_token(client, usera):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": "Home", "tzname": "Asia/Yangon"},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert "authorization token missing" in data["message"]


def test_create_timezone_without_wrong_auth_token(client, usera, userb_auth_token):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": "Home", "tzname": "Asia/Yangon"},
        headers={"Authorization": "Bearer " + userb_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert "you are not allowed to create timezone for other users" in data["message"]


def test_create_timezone_with_wrong_tz_name(client, usera, usera_auth_token):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": "Home", "tzname": "Asia/Yango"},
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "The given timezone is not valid"


def test_create_timezone_user_successful(client, usera, usera_auth_token):
    Timezone.query.delete()  # truncate

    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": "Home", "tzname": "Asia/Yangon"},
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "new timezone added"

    timezones = Timezone.query.filter_by(user_id=usera.uuid).all()
    assert len(timezones) == 1
    assert timezones[0].name == "Home"
    assert timezones[0].user_id == usera.uuid
    assert timezones[0].tzname == "Asia/Yangon"
    assert timezones[0].utcoffset > 0


def test_create_timezone_admin_successful(client, userb, admin_auth_token):
    Timezone.query.delete()  # truncate

    resp = client.post(
        "/users/" + userb.uuid + "/timezones",
        json={"name": "Home", "tzname": "Asia/Yangon"},
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "new timezone added"

    timezones = Timezone.query.filter_by(user_id=userb.uuid).all()
    assert len(timezones) == 1
    assert timezones[0].name == "Home"
    assert timezones[0].user_id == userb.uuid
    assert timezones[0].tzname == "Asia/Yangon"
    assert timezones[0].utcoffset > 0
