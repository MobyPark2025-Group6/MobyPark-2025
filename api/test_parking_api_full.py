# test_parking_api_full.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi.testclient import TestClient
from unittest.mock import patch

from FastApiServer import app
from models.parking_models import SessionStart, SessionStop

client = TestClient(app)

# ---------------------------
# Mock data
# ---------------------------
mock_admin_user = {"username": "admin", "role": "ADMIN"}
mock_normal_user = {"username": "user1", "role": "USER"}
mock_sessions_active = {
    "1": {"licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": None, "user": "user1"}
}
mock_sessions_stopped = {
    "1": {"licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": "01-01-2025 12:00:00", "user": "user1"}
}
mock_parking_lots = [
    {
        "name": "Lot1", 
        "location": "Location1", 
        "capacity": 10, 
        "hourly_rate": 5.0
    }
]

# ---------------------------
# Parking Lot Endpoints
# ---------------------------

@patch("services.parking_service.ParkingService.create_parking_lot")
def test_create_parking_lot_endpoint(mock_service):
    mock_service.return_value = {"message": "Parking lot created successfully", "parking_lot_id": "1"}
    response = client.post("/parking-lots", json={
        "name": "LotX", "location": "LocX", "capacity": 5, "hourly_rate": 3.0
    }, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code in (200, 201)
    assert response.json()["parking_lot_id"] == "1"

@patch("services.parking_service.ParkingService.list_parking_lots")
def test_list_parking_lots_endpoint(mock_service):
    mock_service.return_value = [
        {"message": "Lot retrieved", "parking_lot_id": "1"}
    ]
    response = client.get("/parking-lots", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["parking_lot_id"] == "1"


@patch("services.parking_service.ParkingService.get_parking_lot")
def test_get_parking_lot_endpoint(mock_service):
    mock_service.return_value = {"message": "Lot retrieved", "parking_lot_id": "1"}
    response = client.get("/parking-lots/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["parking_lot_id"] == "1"

@patch("services.parking_service.ParkingService.delete_parking_lot")
def test_delete_parking_lot_endpoint(mock_service):
    mock_service.return_value = {"detail": "Parking lot deleted"}
    response = client.delete("/parking-lots/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Parking lot deleted"

# ---------------------------
# Parking Session Endpoints
# ---------------------------

@patch("services.parking_service.ParkingService.start_parking_session")
def test_start_parking_session_endpoint(mock_service):
    mock_service.return_value = {"message": "Session started successfully", "licenseplate": "XYZ123"}
    response = client.post("/parking-lots/1/sessions/start", json={"licenseplate": "XYZ123"},
                           headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["licenseplate"] == "XYZ123"

@patch("services.parking_service.ParkingService.stop_parking_session")
def test_stop_parking_session_endpoint(mock_service):
    mock_service.return_value = {"message": "Session stopped successfully", "licenseplate": "XYZ123"}
    response = client.post("/parking-lots/1/sessions/stop", json={"licenseplate": "XYZ123"},
                           headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["licenseplate"] == "XYZ123"

@patch("services.parking_service.ParkingService.list_parking_sessions")
def test_list_parking_sessions_endpoint(mock_service):
    mock_service.return_value = [
        {"message": "Session started successfully", "licenseplate": "XYZ123"}
    ]
    response = client.get("/parking-lots/1/sessions", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["licenseplate"] == "XYZ123"


@patch("services.parking_service.ParkingService.get_parking_session")
def test_get_parking_session_endpoint(mock_service):
    mock_service.return_value = {"message": "Session retrieved", "licenseplate": "XYZ123"}
    response = client.get("/parking-lots/1/sessions/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["licenseplate"] == "XYZ123"

@patch("services.parking_service.ParkingService.delete_parking_session")
def test_delete_parking_session_endpoint(mock_service):
    mock_service.return_value = {"detail": "Session deleted"}
    response = client.delete("/parking-lots/1/sessions/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Session deleted"

# ---------------------------
# Permission Tests
# ---------------------------

@patch("services.parking_service.ParkingService.validate_session_token")
def test_normal_user_cannot_create_parking_lot(mock_validate):
    mock_validate.return_value = mock_normal_user
    response = client.post("/parking-lots", json={
        "name": "LotX", "location": "LocX", "capacity": 5, "hourly_rate": 3.0
    }, headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 403

@patch("services.parking_service.get_session")
def test_normal_user_cannot_delete_parking_lot(mock_get_session):
    mock_get_session.return_value = mock_normal_user
    response = client.delete("/parking-lots/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 403

@patch("services.parking_service.get_session")
@patch("services.parking_service.load_json")
def test_normal_user_cannot_delete_other_user_session(mock_load, mock_get_session):
    mock_get_session.return_value = mock_normal_user
    mock_load.return_value = {"1": {"licenseplate": "ABC123", "started": "01-01-2025", "stopped": None, "user": "other_user"}}
    response = client.delete("/parking-lots/1/sessions/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 403

@patch("services.parking_service.get_session")
@patch("services.parking_service.load_parking_lot_data")
@patch("services.parking_service.save_parking_lot_data")
def test_admin_can_delete_parking_lot(mock_save, mock_load, mock_get_session):
    mock_get_session.return_value = mock_admin_user
    mock_load.return_value = {"1": {"name": "Lot1", "location": "Loc1", "capacity": 5, "hourly_rate": 2.0}}
    response = client.delete("/parking-lots/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Parking lot deleted"

@patch("services.parking_service.get_session")
@patch("services.parking_service.load_json")
@patch("services.parking_service.save_data")
def test_admin_can_delete_any_session(mock_save, mock_load, mock_get_session):
    mock_get_session.return_value = mock_admin_user
    mock_load.return_value = {"1": {"licenseplate": "ABC123", "started": "01-01-2025", "stopped": None, "user": "other_user"}}
    response = client.delete("/parking-lots/1/sessions/1", headers={"Authorization": "Bearer testtoken"})
    assert response.status_code == 200
    assert response.json()["detail"] == "Session deleted"

# ---------------------------
# Edge Cases / Error Handling
# ---------------------------

@patch("services.parking_service.ParkingService.validate_session_token")
@patch("services.parking_service.load_json")
def test_start_session_when_already_active(mock_load, mock_validate):
    mock_validate.return_value = mock_normal_user
    mock_load.return_value = mock_sessions_active
    from services.parking_service import ParkingService
    import pytest
    with pytest.raises(Exception) as exc_info:
        ParkingService.start_parking_session("1", SessionStart(licenseplate="XYZ123"), token="token")
    assert "Cannot start a session when another session for this license plate is already active" in str(exc_info.value)

@patch("services.parking_service.ParkingService.validate_session_token")
@patch("services.parking_service.load_json")
def test_stop_session_that_does_not_exist(mock_load, mock_validate):
    mock_validate.return_value = mock_normal_user
    mock_load.return_value = mock_sessions_stopped
    from services.parking_service import ParkingService
    import pytest
    with pytest.raises(Exception) as exc_info:
        ParkingService.stop_parking_session("1", SessionStop(licenseplate="ABC999"), token="token")
    assert "Cannot stop a session when there is no active session for this license plate" in str(exc_info.value)

@patch("services.parking_service.load_parking_lot_data")
def test_get_nonexistent_parking_lot(mock_load):
    mock_load.return_value = {}
    from services.parking_service import ParkingService
    import pytest
    with pytest.raises(Exception) as exc_info:
        ParkingService.get_parking_lot("99", token="token")
    assert "Parking lot not found" in str(exc_info.value)

@patch("services.parking_service.get_session")
@patch("services.parking_service.load_json")
def test_get_nonexistent_session(mock_load, mock_get_session):
    mock_get_session.return_value = mock_normal_user
    mock_load.return_value = {}
    from services.parking_service import ParkingService
    import pytest
    with pytest.raises(Exception) as exc_info:
        ParkingService.get_parking_session("1", "99", token="token")
    assert "Session not found" in str(exc_info.value)

@patch("services.parking_service.get_session")
def test_invalid_session_token(mock_get_session):
    mock_get_session.return_value = None
    from services.parking_service import ParkingService
    import pytest
    with pytest.raises(Exception) as exc_info:
        ParkingService.list_parking_sessions("1", token="invalid")
    assert "Unauthorized" in str(exc_info.value)