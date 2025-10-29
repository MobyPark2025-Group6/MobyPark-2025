import pytest

from models.vehicle_models import Vehicle
from storage_utils import load_vehicle_data, save_data, save_vehicle_data
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
        response = VehicleService.get_all_vehicles_admin_user(TestMobyPark.authorization,"cindy.leenders42")
        assert isinstance(response,list)
        assert len(response) >= 0
        

    def test_change_vehicle(self):
       
        response = VehicleService.ChangeVehicle(
            TestMobyPark.authorization,
            "1",
            Vehicle(
                id="1",
                user_id="1",
                license_plate="76-KQQ-7",
                make="Peugeot",
                model="308",
                color="Brown",
                year=2024,
                created_at="2024-08-13"
            )

        )
        
        assert response["status"] == "Success"
        assert "vehicle" in response
        vehicle = response["vehicle"]
        assert vehicle["model"] == "308"
        assert vehicle["license_plate"] == "76-KQQ-7"
        
    def test_create_vehicle(self):
        vehicle_data = {
            "license_plate" : "12-test-12",
            "make": "test",
        }
        response = VehicleService.CreateVehicle( TestMobyPark.authorization, vehicle_data)
        assert response["status"] == "Success"

    def test_act_on_vehicle(self):
        vehicle_data = {
            "license_plate" : "12-test-12",
            "make": "test",
        }
        response = VehicleService.ActOnVehicle( TestMobyPark.authorization, vehicle_data)
        assert response["status"] == "Success"

    def test_delete_vehicle(self):
        vehicles = load_vehicle_data()
        vehicle = [v for v in vehicles if v.get("license_plate") != "12-test-12"]
        save_vehicle_data(vehicle)

        
        updated_vehicles = load_vehicle_data()
        assert all(v for v in updated_vehicles if v['license_plate'] !="12-test-12")
    





if __name__ == '__main__':
    pytest.main()
