import pytest
import requests

from services.vehicle_service import VehicleService
from services.user_service import *
from models.user_models import * 

class TestMobyPark:
    def __init__(self):
        self.authorization
        
    def test_authenticate_user(self):
        credentials = UserLogin(username="cindy.leenders42", password="password")
        response = UserService.authenticate_user(credentials)
        assert response.message == "User logged in successfully"
        assert isinstance(response.session_token, str)
        assert len(response.session_token) > 0

    def test_get_vehicle_id_reservations(self):
        VehicleService.get_vehicle_history(authorization, vehicle_id) 
        pass
    def test_get_vehicle_id_history(self):
        pass
    def test_get_vehicles_username(self):
        pass
    def test_get_vehicles(self):
        pass
    def test_change_vehicle(self):
        pass
    def test_create_vehicle(self):
        pass
    def test_act_on_vehicle(self):
        pass
    def test_delete_vehicle(self):
        pass
        


if __name__ == '__main__':
    pytest.main()
