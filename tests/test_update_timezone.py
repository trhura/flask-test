from pytz import timezone
from models import Timezone


def test_update_timezone_without_json_body(client, usera):
    resp = client.post("/users/" + usera.uuid + "/timezones/3")
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert data["message"] == "Failed to decode JSON object"


def test_update_timezone_without_any_param(client, usera):
    resp = client.post("/users/" + usera.uuid + "/timezones/3", json={})
    data = resp.get_json()
    assert resp.status_code == 400

    assert data["success"] is False
    assert "is a required property" in data["message"]


def test_update_timezone_without_auth_token(client, usera):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones/3", json={"name": "Thura's Place"}
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_update_timezone_with_invalid_token(client, usera, userb_auth_token, tza1):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones/" + str(tza1.id),
        json={"name": "Thura's Place"},
        headers={
            "Authorization": "Bearer " + userb_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to update timezone for other users"


def test_update_timezone_succesful_name(client, usera, usera_auth_token, tza1):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones/" + str(tza1.id),
        json={"name": "Second name"},
        headers={
            "Authorization": "Bearer " + usera_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "timezone updated successfully"

    tza = Timezone.query.filter_by(user_id=usera.uuid, id=tza1.id).first()
    assert tza.name == "Second name"


def test_update_timezone_succesful_tzname(client, usera, usera_auth_token, tza2):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones/" + str(tza2.id),
        json={"tzname": "Asia/Saigon"},
        headers={
            "Authorization": "Bearer " + usera_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "timezone updated successfully"

    tza = Timezone.query.filter_by(user_id=usera.uuid, id=tza2.id).first()
    assert tza.tzname == "Asia/Saigon"
    assert tza.utcoffset == timezone("Asia/Saigon")._utcoffset.total_seconds()


def test_update_timezone_succesful_admin(client, userb, admin_auth_token, tzb1):
    resp = client.post(
        "/users/" + userb.uuid + "/timezones/" + str(tzb1.id),
        json={"name": "new name", "tzname": "Asia/Taipei"},
        headers={
            "Authorization": "Bearer " + admin_auth_token,
        },
    )
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "timezone updated successfully"

    tza = Timezone.query.filter_by(user_id=userb.uuid, id=tzb1.id).first()
    assert tza.name == "new name"
    assert tza.tzname == "Asia/Taipei"
    assert tza.utcoffset == timezone("Asia/Taipei")._utcoffset.total_seconds()
