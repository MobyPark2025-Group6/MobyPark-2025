# test_parking_api_full.py
import sys, os
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from unittest.mock import patch
import pytest

from api.FastApiServer import app
from api.models.parking_models import SessionStart, SessionStop

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

@pytest.fixture
def system_token():
    return "system-token"

@pytest.fixture
def licenseplate():
    return "AUTO123"

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

@patch("services.parking_service.ParkingService.validate_session_token")
@patch("services.parking_service.get_item_db")
@patch("services.parking_service.save_parking_lot")
def test_admin_update_parking_lot(mock_save, mock_get, mock_validate):
    # Mock admin user
    mock_validate.return_value = {"username": "admin", "role": "ADMIN"}

    # Mock bestaande parkeerplaats
    mock_get.return_value = [
        {"id": "1", "name": "Lot1", "location": "Loc1", "capacity": 5, "hourly_rate": 2.0}
    ]

    from services.parking_service import ParkingService

    updates = {"name": "Lot1-updated", "capacity": 10}
    result = ParkingService.update_parking_lot("1", updates, token="admintoken")

    assert result["parking_lot_id"] == "1"
    # Controleer dat save is aangeroepen
    mock_save.change_plt.assert_called_once()


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

@patch("services.parking_service.ParkingService.validate_session_token")
@patch("services.parking_service.get_item_db")
@patch("services.parking_service.save_parking_sessions")
def test_admin_update_session(mock_save, mock_get, mock_validate):
    # Mock admin
    mock_validate.return_value = {"username": "admin", "role": "ADMIN"}
    
    # Bestaande session
    mock_get.return_value = [
        {"id": "1", "licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": None, "user": "user1"}
    ]

    from services.parking_service import ParkingService

    updates = {"stopped": "01-01-2025 12:00:00", "user": "user2"}
    updated_session = ParkingService.update_parking_session("1", "1", updates, token="admintoken")

    assert updated_session["stopped"] == "01-01-2025 12:00:00"
    assert updated_session["user"] == "user2"
    mock_save.change_parking_sessions.assert_called_once()

@patch("services.parking_service.get_item_db", return_value=[])
@patch("services.parking_service.save_parking_sessions")
def test_auto_start_parking(mock_save, mock_get):
    from services.parking_service import ParkingService
    licenseplate = "AUTO123"
    result = ParkingService.auto_start_parking("1", licenseplate)
    assert result.message == "Session started successfully"
    assert result.licenseplate == licenseplate

@patch("services.parking_service.get_item_db", return_value=[
    {"id":"1","licenseplate": "AUTO123", "started": "2025-12-09 10:00:00", "stopped": 'None', "user": "system"}
])
@patch("services.parking_service.save_parking_sessions")
def test_auto_stop_parking(mock_save, mock_get):
    from services.parking_service import ParkingService
    licenseplate = "AUTO123"
    result = ParkingService.auto_stop_parking("1", licenseplate)
    assert result.message == "Session stopped successfully"
    assert result.licenseplate == licenseplate

@patch("services.parking_service.get_item_db", return_value=[
    {"id":"1","licenseplate": "AUTO123", "started": "2025-12-09 10:00:00", "stopped": None, "user": "system"}
])
def test_auto_start_existing_session_raises(mock_get, licenseplate):
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        ParkingService.auto_start_parking("1", licenseplate)
    assert "Cannot start a session when another session for this license plate is already active" in str(exc.value)

@patch("services.parking_service.get_item_db", return_value=[])
def test_auto_stop_nonexistent_session_raises(mock_get, licenseplate):
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        ParkingService.auto_stop_parking("1", licenseplate)
    assert "Cannot stop a session when there is no active session for this license plate" in str(exc.value)


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
@patch("services.parking_service.save_parking_sessions")
@patch("services.parking_service.save_parking_lot")
def test_admin_permissions(mock_save_lot, mock_save_sess, mock_get_session, auth_header):
    mock_get_session.return_value = mock_admin_user
    resp1 = client.delete("/parking-lots/1", headers=auth_header())
    resp2 = client.delete("/parking-lots/1/sessions/1", headers=auth_header())
    for resp, detail in ((resp1, "Parking lot deleted"), (resp2, "Session deleted")):
        assert resp.status_code == 200
        assert resp.json()["detail"] == detail

@patch("services.parking_service.ParkingService.validate_session_token")
def test_normal_user_cannot_update_lot(mock_validate):
    # Mock normale user
    mock_validate.return_value = {"username": "user1", "role": "USER"}

    from services.parking_service import ParkingService
    updates = {"name": "Lot1-updated"}

    with pytest.raises(Exception) as exc:
        ParkingService.update_parking_lot("1", updates, token="usertoken")
    
    assert "Access denied" in str(exc.value)


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
@patch("services.parking_service.get_item_db")
def test_session_errors(mock_get, mock_validate, method, session_data, session_obj, expected_msg):
    mock_validate.return_value = mock_normal_user
    # Flatten dict session_data values to list for get_item_db return
    vals = list(session_data.values()) if isinstance(session_data, dict) else session_data
    mock_get.return_value = vals
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        if method == "stop_parking_session":
            getattr(ParkingService, method)("1", session_obj, None, token="token")
        else:
            getattr(ParkingService, method)("1", session_obj, token="token")
    assert expected_msg in str(exc.value)

@patch("services.parking_service.get_item_db")
def test_get_nonexistent_lot(mock_get):
    mock_get.return_value = []
    from services.parking_service import ParkingService
    with pytest.raises(Exception) as exc:
        ParkingService.get_parking_lot("99", token="token")
    assert "Parking lot not found" in str(exc.value)

@patch("services.parking_service.get_session")
@patch("services.parking_service.get_item_db")
def test_get_nonexistent_session(mock_get, mock_get_session):
    mock_get_session.return_value = mock_normal_user
    mock_get.return_value = []
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
