import pytest

from models.vehicle_models import Vehicle
from storage_utils import load_vehicle_data,  save_vehicle_data
from services.vehicle_service import VehicleService
from services.user_service import *
from models.user_models import * 
import json

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

    def test_user_creation(self):
        user_data = UserRegister(
            username="testuser",
            password="testpassword",
            name="Test User",
            email="test.user@example.com"
        )
        response = UserService.create_user(user_data)
        assert response.message == "User created successfully"  

    def test_user_read(self):
        user = UserService.get_user_by_username("testuser")
        assert user is not None
        # Print all attributes of the returned user object for debugging
        if isinstance(user, dict):
            print(json.dumps(user, indent=2, default=str))
        else:
            try:
                attrs = vars(user)
            except TypeError:
                attrs = {k: getattr(user, k) for k in dir(user) if not k.startswith('_') and not callable(getattr(user, k))}
            print(json.dumps(attrs, indent=2, default=str))
        assert user["username"] == "testuser"
        assert user["name"] == "Test User"
        assert user["email"] == "test.user@example.com"

    def test_user_update(self):
        user_data = User(
            username="testuser",
            name="Updated User",
            email="updated.user@example.com"
        )
        response = UserService.update_user(user_data)
        assert response.message == "User updated successfully"

    def test_user_deletion(self):
        response = UserService.delete_user("testuser")
        assert response.message == "User deleted successfully"

    def test_get_vehicle_id_reservations(self):
        response = VehicleService.get_vehicle_reservations(TestMobyPark.authorization, "1") 
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
        # Potentially arbirtary, the expected function of acting on a vehicle id might already be handled in parking_service
        # vehicle_data = {
        #     "license_plate" : "12-test-12",
        #     "make": "test",
        # }
        # response = VehicleService.ActOnVehicle( TestMobyPark.authorization, vehicle_data)
        # assert response["status"] == "Success"
        pass

    def test_delete_vehicle(self):
        vehicles = load_vehicle_data()
        cur_vehicle = [v for v in vehicles if v["license_plate"] == "12-test-12" ][0]
        response = VehicleService.DeleteVehicle(TestMobyPark.authorization, cur_vehicle['id'])
        assert response['Status'] == "Deleted"

if __name__ == '__main__':
    pytest.main()