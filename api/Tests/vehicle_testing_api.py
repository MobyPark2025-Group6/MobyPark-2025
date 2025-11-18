from types import SimpleNamespace
from unittest.mock import patch
import pytest
from unittest.mock import patch
from models.vehicle_models import Vehicle
from storage_utils import load_vehicle_data,  save_vehicle_data
from services.vehicle_service import VehicleService
from services.user_service import *
from models.user_models import * 
import json
import pprint
# Mock data 
mock_normal_user = {"username": "user1", "role": "USER"}
mock_admin_user = {"username": "admin1", "role": "ADMIN"}

mock_sessions_active = {
    "1": {"licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": None, "user": "user1"},
    "2": {"licenseplate": "ABC123", "started": "02-04-2025 10:00:00", "stopped": None, "user": "user1"}
}


mock_user_vehicles = [
    {"id": "1", "user_id": "1", "license_plate": "76-ACB-7", "make": "BMW", "model": "308", "color": "Brown", "year": 2024, "created_at": "2024-04-13"},
    {"id": "2", "user_id": "1", "license_plate": "76-BCA-7", "make": "Peugeot", "model": "123", "color": "Blue", "year": 2020, "created_at": "2024-03-13"},
    {"id": "3", "user_id": "2", "license_plate": "76-QAU-7", "make": "CAR", "model": "213", "color": "Yellow", "year": 1800, "created_at": "2024-02-13"},
    {"id": "4", "user_id": "3", "license_plate": "76-PSL-7", "make": "Peugeot", "model": "3028", "color": "Red", "year": 2000, "created_at": "2024-01-13"}
]

@pytest.fixture
def auth_header():
    """Return a function to generate Authorization headers with a Bearer token."""
    def _auth(token="testtoken"):
        return {"Authorization": f"Bearer {token}"}
    return _auth

from types import SimpleNamespace
from unittest.mock import patch

def test_get_vehicle_id_reservations_mocked(auth_header):

    token = "fake-token-1"
    vid = "1"

    # Sample reservations: one matching vid, one other
    fake_reservations = [
        {"id": "r1", "vehicle_id": "1", "licenseplate": "XYZ123", "user": "user1", "started": "2025-01-01 10:00:00"},
        {"id": "r2", "vehicle_id": "2", "licenseplate": "ABC999", "user": "user2", "started": "2025-01-02 10:00:00"}
    ]

    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.checkForVehicle") as mock_check, \
         patch("services.vehicle_service.load_parking_lot_data") as mock_load_parking:

        # Make the validator accept any token and return a session user dict
        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}

        # Make the vehicle-existence check a no-op (so it won't raise HTTPException)
        mock_check.return_value = None

        # Return the fake reservations list when the service loads parking data
        mock_load_parking.return_value = fake_reservations

        # Call the real service
        result = VehicleService.get_vehicle_reservations(token, vid)

        # Assertions
        assert isinstance(result, list)
        assert len(result) == 1                         # only one item matches vehicle_id == "1"
        assert result[0]["vehicle_id"] == vid
        assert result[0]["licenseplate"] == "XYZ123"

        # Verify the mocks were used as expected
        mock_validate.assert_called_once_with(token)
        mock_check.assert_called_once_with(mock_validate.return_value, vid)
        mock_load_parking.assert_called_once()


def test_get_vehicle_id_history_mock(auth_header):
    token = "fake-token-1"
    vid = "1"


    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.checkForVehicle") as mock_check :
        
        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_check.return_value = None

        result = VehicleService.get_vehicle_history(token, vid)
        assert isinstance(result, list)
        assert len(result) >= 1                   # only one item matches vehicle_id == "1"
      
        mock_validate.assert_called_once_with(token)
        mock_check.assert_called_once_with(mock_validate.return_value, vid)
    

def test_get_all_vehicles_for_user_mocked():
    token = "fake-token"
    fake_user_vehicles = [
        {"id": "1", "user_id": "1", "license_plate": "76-ACB-7", "make": "BMW", "model": "308", "color": "Brown", "year": 2024, "created_at": "2024-04-13"},
        {"id": "2", "user_id": "1", "license_plate": "76-BCA-7", "make": "Peugeot", "model": "123", "color": "Blue", "year": 2020, "created_at": "2024-03-13"}
    ]

    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.user_service.UserService.user_exists") as mock_user_exists, \
         patch("services.vehicle_service.VehicleService.getUserVehicles") as mock_get_user_vehicles:

        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_user_exists.return_value = None
        mock_get_user_vehicles.return_value = fake_user_vehicles

        result = VehicleService.get_all_vehicles(token)

        # Assertions
        assert result == fake_user_vehicles
        mock_validate.assert_called_once_with(token)
        mock_user_exists.assert_called_once_with("user1")
        mock_get_user_vehicles.assert_called_once_with("1")

def test_get_vehicles_admin_mocked():
    token = "admin-fake-token"
    fake_response = [
        {"id": "1", "user_id": "1", "license_plate": "AA-111-1"},
        {"id": "2", "user_id": "2", "license_plate": "BB-222-2"}
    ]

    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.get_all_vehicles_admin_user") as mock_admin_list:

        mock_validate.return_value = {"id": "admin", "username": "admin1", "role": "ADMIN"}
        mock_admin_list.return_value = fake_response

        result = VehicleService.get_all_vehicles_admin_user(token, "some.user")

        assert result == fake_response
        mock_validate.assert_called_once_with(token)
        mock_admin_list.assert_called_once_with(token, "some.user")


def test_change_vehicle_mocked():
    token = "fake-token"
    vehicle_payload = Vehicle(
        id="1",
        user_id="1",
        license_plate="76-KQQ-7",
        make="Peugeot",
        model="308",
        color="Brown",
        year=2024,
        created_at="2024-08-13"
    )

    fake_response = {"status": "Success", "vehicle": vehicle_payload.__dict__}

    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.ChangeVehicle") as mock_change:

        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_change.return_value = fake_response

        resp = VehicleService.ChangeVehicle(token, "1", vehicle_payload)

        assert resp["status"] == "Success"
        assert "vehicle" in resp
        assert resp["vehicle"]["license_plate"] == "76-KQQ-7"
        mock_validate.assert_called_once_with(token)
        mock_change.assert_called_once_with(token, "1", vehicle_payload)


def test_create_vehicle_mocked():
    token = "fake-token"
    vehicle_data = {"license_plate": "12-test-12", "make": "test"}
    fake_response = {"status": "Success", "vehicle": {"id": "99", **vehicle_data}}

    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.CreateVehicle") as mock_create:

        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_create.return_value = fake_response

        resp = VehicleService.CreateVehicle(token, vehicle_data)

        assert resp["status"] == "Success"
        assert resp["vehicle"]["license_plate"] == "12-test-12"
        mock_validate.assert_called_once_with(token)
        mock_create.assert_called_once_with(token, vehicle_data)


def test_delete_vehicle_mocked():
    token = "fake-token"
    fake_vehicle_id = "99"

    with patch("services.validation_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.DeleteVehicle") as mock_delete:

        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_delete.return_value = {"Status": "Deleted"}

        resp = VehicleService.DeleteVehicle(token, fake_vehicle_id)

        assert resp["Status"] == "Deleted"
        mock_validate.assert_called_once_with(token)
        mock_delete.assert_called_once_with(token, fake_vehicle_id)
