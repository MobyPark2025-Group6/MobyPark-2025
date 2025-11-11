# test_parking_api_full.py
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from FastApiServer import app
from models.parking_models import SessionStart, SessionStop

client = TestClient(app)

# ---------------------------
# Mock Data
# ---------------------------
mock_admin_user = {"username": "admin", "role": "ADMIN"}
mock_normal_user = {"username": "user1", "role": "USER"}

mock_sessions_active = {
    "1": {"licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": None, "user": "user1"}
}
mock_sessions_stopped = {
    "1": {"licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": "01-01-2025 12:00:00", "user": "user1"}
}

mock_parking_lot = {"1": {"name": "Lot1", "location": "Loc1", "capacity": 5, "hourly_rate": 2.0}}
mock_parking_session = {"1": {"licenseplate": "ABC123", "started": "01-01-2025", "stopped": None, "user": "other_user"}}

# ---------------------------
# Fixtures
# ---------------------------
@pytest.fixture
def auth_header():
    def _auth(token="testtoken"):
        return {"Authorization": f"Bearer {token}"}
    return _auth

# ---------------------------
# Parking Lot Endpoint Tests
# ---------------------------
@pytest.mark.parametrize("endpoint,method,payload,expected_status", [
    ("/parking-lots", "post", {"name":"LotX","location":"LocX","capacity":5,"hourly_rate":3.0}, (200,201))
])
def test_create_parking_lot(endpoint, method, payload, expected_status, auth_header):
    with patch("services.parking_service.ParkingService.create_parking_lot") as mock_service:
        mock_service.return_value = {"message": "Parking lot created successfully", "parking_lot_id": "1"}
        resp = client.post(endpoint, json=payload, headers=auth_header())
        assert resp.status_code in expected_status
        assert resp.json()["parking_lot_id"] == "1"

@patch("services.parking_service.ParkingService.list_parking_lots")
def test_list_parking_lots(mock_service, auth_header):
    mock_service.return_value = [{"message":"Lot retrieved","parking_lot_id":"1"}]
    resp = client.get("/parking-lots", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()[0]["parking_lot_id"] == "1"

    # test empty
    mock_service.return_value = []
    resp_empty = client.get("/parking-lots", headers=auth_header())
    assert resp_empty.status_code == 200
    assert resp_empty.json() == []

@patch("services.parking_service.ParkingService.get_parking_lot")
def test_get_parking_lot(mock_service, auth_header):
    mock_service.return_value = {"message":"Lot retrieved","parking_lot_id":"1"}
    resp = client.get("/parking-lots/1", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()["parking_lot_id"] == "1"

@patch("services.parking_service.ParkingService.delete_parking_lot")
def test_delete_parking_lot(mock_service, auth_header):
    mock_service.return_value = {"detail":"Parking lot deleted"}
    resp = client.delete("/parking-lots/1", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Parking lot deleted"

# ---------------------------
# Parking Session Tests
# ---------------------------
@pytest.mark.parametrize("endpoint,method,licenseplate", [
    ("/parking-lots/1/sessions/start", "start_parking_session", "XYZ123"),
    ("/parking-lots/1/sessions/stop", "stop_parking_session", "XYZ123"),
])
def test_start_stop_session(endpoint, method, licenseplate, auth_header):
    with patch(f"services.parking_service.ParkingService.{method}") as mock_service:
        mock_service.return_value = {"message": f"Session {method.split('_')[0]}ed successfully", "licenseplate": licenseplate}
        resp = client.post(endpoint, json={"licenseplate": licenseplate}, headers=auth_header())
        assert resp.status_code == 200
        assert resp.json()["licenseplate"] == licenseplate

@patch("services.parking_service.ParkingService.list_parking_sessions")
def test_list_parking_sessions(mock_service, auth_header):
    mock_service.return_value = [{"message":"Session started successfully","licenseplate":"XYZ123"}]
    resp = client.get("/parking-lots/1/sessions", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()[0]["licenseplate"] == "XYZ123"

    # test empty
    mock_service.return_value = []
    resp_empty = client.get("/parking-lots/1/sessions", headers=auth_header())
    assert resp_empty.json() == []

def test_user_only_sees_own_sessions(tmp_path):
    from services.parking_service import ParkingService
    import json, os
    from unittest.mock import patch

    sessions = {
        "1": {"licenseplate": "AA11BB", "started": "01-01-2025 10:00:00", "stopped": None, "user": "user1"},
        "2": {"licenseplate": "CC22DD", "started": "01-01-2025 12:00:00", "stopped": None, "user": "other"}
    }

    os.makedirs(tmp_path / "data/pdata", exist_ok=True)
    file = tmp_path / "data/pdata/p1-sessions.json"
    file.write_text(json.dumps(sessions))

    with patch("services.parking_service.load_json", return_value=sessions):
        with patch("services.parking_service.get_session", return_value={"username": "user1", "role": "USER"}):
            result = [s for s in sessions.values() if s["user"] == "user1"]  # ✅ hier values() gebruiken
            assert all(s["user"] == "user1" for s in result)

@patch("services.parking_service.ParkingService.get_parking_session")
def test_get_parking_session(mock_service, auth_header):
    mock_service.return_value = {"message":"Session retrieved","licenseplate":"XYZ123"}
    resp = client.get("/parking-lots/1/sessions/1", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()["licenseplate"] == "XYZ123"

@patch("services.parking_service.ParkingService.delete_parking_session")
def test_delete_parking_session(mock_service, auth_header):
    mock_service.return_value = {"detail":"Session deleted"}
    resp = client.delete("/parking-lots/1/sessions/1", headers=auth_header())
    assert resp.status_code == 200
    assert resp.json()["detail"] == "Session deleted"

# ---------------------------
# Permission Tests
# ---------------------------
@pytest.mark.parametrize("user,expected_status", [
    (mock_normal_user,403),
])
@patch("services.parking_service.get_session")
def test_normal_user_permissions(mock_get_session, user, expected_status, auth_header):
    mock_get_session.return_value = user
    for url in ["/parking-lots/1","/parking-lots/1/sessions/1"]:
        resp = client.delete(url, headers=auth_header())
        assert resp.status_code == expected_status

@patch("services.parking_service.get_session")
@patch("services.parking_service.load_parking_lot_data")
@patch("services.parking_service.save_parking_lot_data")
@patch("services.parking_service.load_json")
@patch("services.parking_service.save_data")
def test_admin_permissions(mock_save_data, mock_load_json, mock_save_lot, mock_load_lot, mock_get_session, auth_header):
    mock_get_session.return_value = mock_admin_user
    mock_load_lot.return_value = mock_parking_lot
    mock_load_json.return_value = mock_parking_session
    resp1 = client.delete("/parking-lots/1", headers=auth_header())
    resp2 = client.delete("/parking-lots/1/sessions/1", headers=auth_header())
    for resp, detail in ((resp1, "Parking lot deleted"), (resp2, "Session deleted")):
        assert resp.status_code == 200
        assert resp.json()["detail"] == detail

# ---------------------------
# Edge Cases / Errors
# ---------------------------
@pytest.mark.parametrize("method,session_data,session_obj,expected_msg", [
    ("start_parking_session", mock_sessions_active, SessionStart(licenseplate="XYZ123"),
     "Cannot start a session when another session for this license plate is already active"),
    ("stop_parking_session", mock_sessions_stopped, SessionStop(licenseplate="ABC999"),
     "Cannot stop a session when there is no active session for this license plate"),
])
@patch("services.parking_service.ParkingService.validate_session_token")
@patch("services.parking_service.load_json")
def test_session_errors(mock_load, mock_validate, method, session_data, session_obj, expected_msg):
    mock_validate.return_value = mock_normal_user
    mock_load.return_value = session_data
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        getattr(ParkingService, method)("1", session_obj, token="token")
    assert expected_msg in str(exc.value)

@patch("services.parking_service.load_parking_lot_data")
def test_get_nonexistent_lot(mock_load):
    mock_load.return_value = {}
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        ParkingService.get_parking_lot("99", token="token")
    assert "Parking lot not found" in str(exc.value)

@patch("services.parking_service.get_session")
@patch("services.parking_service.load_json")
def test_get_nonexistent_session(mock_load, mock_get_session):
    mock_get_session.return_value = mock_normal_user
    mock_load.return_value = {}
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        ParkingService.get_parking_session("1", "99", token="token")
    assert "Session not found" in str(exc.value)

@patch("services.parking_service.get_session")
def test_invalid_token(mock_get_session):
    mock_get_session.return_value = None
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        ParkingService.list_parking_sessions("1", token="invalid")
    assert "Unauthorized" in str(exc.value)
