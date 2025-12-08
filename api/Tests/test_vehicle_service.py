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
mock_normal_user = {"id": "1", "username": "user1", "role": "USER"}
mock_admin_user = {"id": "2","username": "admin1", "role": "ADMIN"}

mock_sessions_active = {
    "1": {"licenseplate": "XYZ123", "started": "01-01-2025 10:00:00", "stopped": None, "user": "user1"},
    "2": {"licenseplate": "ABC123", "started": "02-04-2025 10:00:00", "stopped": None, "user": "user1"},
    "3": {"licenseplate": "AzC123", "started": "02-14-2025 20:00:00", "stopped": None, "user": "admin1"}
}


mock_user_vehicles = [
    {"id": "1", "user_id": "1", "license_plate": "76-ACB-7", "make": "BMW", "model": "308", "color": "Brown", "year": 2024, "created_at": "2024-04-13"},
    {"id": "2", "user_id": "1", "license_plate": "76-BCA-7", "make": "Peugeot", "model": "123", "color": "Blue", "year": 2020, "created_at": "2024-03-13"},
    {"id": "3", "user_id": "2", "license_plate": "76-QAU-7", "make": "CAR", "model": "213", "color": "Yellow", "year": 1800, "created_at": "2024-02-13"},
    {"id": "4", "user_id": "3", "license_plate": "76-PSL-7", "make": "Peugeot", "model": "3028", "color": "Red", "year": 2000, "created_at": "2024-01-13"}
]

mock_parking_lot = {"1": {"name": "Lot1", "location": "Loc1", "capacity": 5, "hourly_rate": 2.0}}

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
      
        mock_get_user_vehicles.assert_called_once_with("1")

def test_get_all_vehicles_admin_lookup():
    token = "fake-token"
    vehicle_list_for_user1 = [
            {"id": "1", "user_id": "1", "license_plate": "76-ACB-7", "make": "BMW", "model": "308", "color": "Brown", "year": 2024, "created_at": "2024-04-13"},
            {"id": "2", "user_id": "1", "license_plate": "76-BCA-7", "make": "Peugeot", "model": "123", "color": "Blue", "year": 2020, "created_at": "2024-03-13"}
            ]

    with patch("services.vehicle_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.ValidationService.check_valid_admin") as mock_is_admin, \
         patch("services.user_service.UserService.user_exists") as mock_user_exists, \
         patch("services.vehicle_service.VehicleService.getUserVehicles") as mock_get_vehicles:

        mock_validate.return_value =  {"licenseplate": "AzC123", "started": "02-14-2025 20:00:00", "stopped": None, "user": "admin1"}
        mock_is_admin.return_value = True
        mock_user_exists.return_value = mock_normal_user
        mock_get_vehicles.return_value = vehicle_list_for_user1

        resp = VehicleService.get_all_vehicles(token, user_name="user1")

        assert resp == vehicle_list_for_user1
        mock_validate.assert_called_once_with(token)
        mock_get_vehicles.assert_called_once_with("1")


def test_change_vehicle_mocked():
    token = "fake-token"
    with patch("services.vehicle_service.load_vehicle_data") as mock_load, \
     patch("services.vehicle_service.ValidationService.validate_session_token") as mock_validate, \
     patch("services.vehicle_service.VehicleService.checkForVehicle") as mock_vehicle_check , \
     patch("services.vehicle_service.save_vehicle_data") as mock_save : 
        
        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_load.return_value = mock_user_vehicles
        mock_vehicle_check.return_value = True 

        updated_vehicle_data =  {"id": "1", "user_id": "1", "license_plate": "71-XYZ-7", "make": "FORD", "model": "102", "color": "RED", "year": 1900, "created_at": "2024-04-13"}
        mock_save.return_value =  [
            {"id": "1", "user_id": "1", "license_plate": "71-XYZ-7", "make": "FORD", "model": "102", "color": "RED", "year": 1900, "created_at": "2024-04-13"},
            {"id": "2", "user_id": "1", "license_plate": "76-BCA-7", "make": "Peugeot", "model": "123", "color": "Blue", "year": 2020, "created_at": "2024-03-13"},
            {"id": "3", "user_id": "2", "license_plate": "76-QAU-7", "make": "CAR", "model": "213", "color": "Yellow", "year": 1800, "created_at": "2024-02-13"},
            {"id": "4", "user_id": "3", "license_plate": "76-PSL-7", "make": "Peugeot", "model": "3028", "color": "Red", "year": 2000, "created_at": "2024-01-13"}
        ]
        resp = VehicleService.change_vehicle(token, "1", updated_vehicle_data)
        assert resp["status"] == "Success"
        assert updated_vehicle_data in mock_save.return_value
        mock_save.assert_called_once()
        assert updated_vehicle_data in mock_save.call_args[0][0]


def test_create_vehicle_mocked():
    token = "fake-token"
    new_vehicle = {"user_id" : "1", "license_plate": "76-ACB-7", "make": "BMW", "model": "308", "color": "Brown", "year": 224, "created_at": "2020-04-13"}
    with patch("services.vehicle_service.VehicleService.check_for_liscense_id") as mock_liscenseid_check, \
         patch("services.vehicle_service.VehicleService.check_for_parameters") as mock_param_check, \
         patch("services.vehicle_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.load_json") as mock_vehicle_load, \
         patch("services.vehicle_service.save_vehicle_data") as mock_save : 
            
            mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
       
            mock_vehicle_load.return_value = mock_user_vehicles
            mock_param_check.return_value = None
            mock_liscenseid_check.return_value = None
            mock_save.return_value = [
                {"id": "1", "user_id": "1", "license_plate": "76-ACB-7", "make": "BMW", "model": "308", "color": "Brown", "year": 2024, "created_at": "2024-04-13"},
                {"id": "2", "user_id": "1", "license_plate": "76-BCA-7", "make": "Peugeot", "model": "123", "color": "Blue", "year": 2020, "created_at": "2024-03-13"},
                {"id": "3", "user_id": "2", "license_plate": "76-QAU-7", "make": "CAR", "model": "213", "color": "Yellow", "year": 1800, "created_at": "2024-02-13"},
                {"id": "4", "user_id": "3", "license_plate": "76-PSL-7", "make": "Peugeot", "model": "3028", "color": "Red", "year": 2000, "created_at": "2024-01-13"}

            ]

            resp = VehicleService.create_vehicle(token, new_vehicle)
            assert resp["status"] == "Success"
            mock_validate.assert_called_once_with(token)

            mock_param_check.assert_called_once_with(new_vehicle)
            mock_liscenseid_check.assert_called_once_with("76ACB7", mock_normal_user)
            mock_save.assert_called_once()

            saved_list = mock_save.call_args[0][0]
            assert any(v["license_plate"] == "76-ACB-7" for v in saved_list)

    

def test_delete_vehicle_mocked():
    token = "fake-token"
    fake_vehicle_id = "1"

    # initial vehicle list and expected remaining after delete
    initial = list(mock_user_vehicles)
    remaining = [v for v in initial if v["id"] != fake_vehicle_id]

    with patch("services.vehicle_service.ValidationService.validate_session_token") as mock_validate, \
         patch("services.vehicle_service.VehicleService.checkForVehicle") as mock_check, \
         patch("services.vehicle_service.load_vehicle_data") as mock_load, \
         patch("services.vehicle_service.save_vehicle_data") as mock_save:

        # First load returns the initial list, second load (after save) should return remaining
        mock_load.side_effect = [initial, remaining]

        mock_validate.return_value = {"id": "1", "username": "user1", "role": "USER"}
        mock_check.return_value = None
        mock_save.return_value = None

        resp = VehicleService.delete_vehicle(token, fake_vehicle_id)

        assert resp["Status"] == "Deleted"
        mock_validate.assert_called_once_with(token)
        mock_check.assert_called_once_with(mock_validate.return_value, fake_vehicle_id)

        # ensure save was called with the remaining list (no deleted vehicle)
        mock_save.assert_called_once()
        saved_list = mock_save.call_args[0][0]
        assert all(v["id"] != fake_vehicle_id for v in saved_list)
