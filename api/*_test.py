import pytest
import requests

from services.vehicle_service import VehicleService
from services.user_service import *
from models.user_models import * 

authorization = None 
class TestMobyPark:

    authorization = None 
    def test_authenticate_user(self):
        credentials = UserLogin(username="cindy.leenders42", password="password")
        response = UserService.authenticate_user(credentials)
        TestMobyPark.authorization = response.session_token
        assert response.message == "User logged in successfully"
        assert isinstance(response.session_token, str)
        assert len(response.session_token) > 0

    def test_get_vehicle_id_reservations(self):
        response = VehicleService.get_vehicle_history(TestMobyPark.authorization, "1") 
        assert response != None

    def test_get_vehicle_id_history(self):
        response = VehicleService.get_vehicle_history(TestMobyPark.authorization, "1") 
        assert response != None

    def test_get_vehicles_username(self):
        response = VehicleService.get_all_vehicles(TestMobyPark.authorization)
        assert isinstance(response,list)
        assert len(response) >= 0

    def test_get_vehicles_admin(self):
        # implement with admin in mind
        # response = VehicleService.get_all_vehicles_admin_user(TestMobyPark.authorization,"cindy.leenders42")
        # assert isinstance(response,list)
        # assert response.len >= 0
        pass

    def test_change_vehicle(self):
        response = VehicleService.ChangeVehicle(
             TestMobyPark.authorization,
            vid="1",
            license_plate="76-KQQ-7",
            name="308"
        )
        assert response["status"] == "Success"
        assert "vehicle" in response
        vehicle = response["vehicle"]
        assert vehicle["name"] == "308"
        assert vehicle["license_plate"] == "76-KQQ-7"
        
    def test_create_vehicle(self):
        vehicle_data = {
            "license_plate" : "12-test-12",
            "name": "test",
        }
        response = VehicleService.CreateVehicle( TestMobyPark.authorization, vehicle_data)
        assert response["status"] == "Success"

    def test_act_on_vehicle(self):
        vehicle_data = {
            "license_plate" : "12-test-12",
            "name": "test",
        }
        response = VehicleService.CreateVehicle( TestMobyPark.authorization, vehicle_data)
        assert response["status"] == "Success"
    def test_delete_vehicle(self):
        pass
        


if __name__ == '__main__':
    pytest.main()
