from models import Timezone


def test_delete_timezone_without_auth_token(client, usera, tza1):
    resp = client.delete("/users/" + usera.uuid + "/timezones/" + str(tza1.id))
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_delete_timezone_with_invalid_id(client, usera, usera_auth_token):
    resp = client.delete(
        "/users/" + usera.uuid + "/timezones/999",
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 404

    assert data["success"] is False
    assert data["message"] == "unable to find specified timezone"


def test_delete_timezone_with_invalid_token(client, usera, tza1, userb_auth_token):
    resp = client.delete(
        "/users/" + usera.uuid + "/timezones/" + str(tza1.id),
        headers={"Authorization": "Bearer " + userb_auth_token},
    )
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "you are not allowed to delete timezone for other users"


def test_delete_timezone_successful(client, randname, usera, usera_auth_token):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": randname, "tzname": "Asia/Tehran"},
        headers={"Authorization": "Bearer " + usera_auth_token},
    )
    assert resp.status_code == 200

    tz = Timezone.query.filter_by(user_id=usera.uuid).first()
    assert tz.name == randname

    resp = client.delete(
        "/users/" + usera.uuid + "/timezones/" + str(tz.id),
        headers={"Authorization": "Bearer " + usera_auth_token},
    )

    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "the timezone has been deleted"

    tz = Timezone.query.filter_by(user_id=usera.uuid).first()
    assert tz is None


def test_delete_timezone_successful_admin(client, randname, usera, admin_auth_token):
    resp = client.post(
        "/users/" + usera.uuid + "/timezones",
        json={"name": randname, "tzname": "Asia/Tehran"},
        headers={"Authorization": "Bearer " + admin_auth_token},
    )
    assert resp.status_code == 200

    tz = Timezone.query.filter_by(user_id=usera.uuid).first()
    assert tz.name == randname

    resp = client.delete(
        "/users/" + usera.uuid + "/timezones/" + str(tz.id),
        headers={"Authorization": "Bearer " + admin_auth_token},
    )

    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert data["message"] == "the timezone has been deleted"

    tz = Timezone.query.filter_by(user_id=usera.uuid).first()
    assert tz is None
