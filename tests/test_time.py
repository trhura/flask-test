def test_get_time_without_auth_token(client, usera):
    resp = client.get("/time")
    data = resp.get_json()
    assert resp.status_code == 401

    assert data["success"] is False
    assert data["message"] == "authorization token missing"


def test_get_time_without_any_timezone(client, usera_auth_token):
    resp = client.get("/time", headers={"Authorization": "Bearer " + usera_auth_token})
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["time"]) == 0


def test_get_time_with_timezones(client, usera_auth_token, tza1, tza2):
    resp = client.get("/time", headers={"Authorization": "Bearer " + usera_auth_token})
    data = resp.get_json()
    assert resp.status_code == 200

    assert data["success"] is True
    assert len(data["time"]) == 2

    assert "Yangon City" in data["time"].keys()
    assert "Seoul City" in data["time"].keys()
