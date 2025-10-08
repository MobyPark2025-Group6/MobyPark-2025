from fastapi import HTTPException, status
import json
from api.models.user_models import User
from api.storage_utils import load_json
from validation_service import ValidationService
from storage_utils import load_vehicle_data
from user_service import UserService
class VehicleService:
    @staticmethod
    def checkForVehicle(session_user : User , Vid : str):
        """Check if the vehicle exists"""
        vehicles = load_vehicle_data
        uvehicles = vehicles.get(session_user["username"], {})
        if not Vid in uvehicles:
              raise HTTPException(
                status_code=status.HTTP_404_FORBIDDEN,
                detail="Not Found"
            )
        

    #Post
    @staticmethod
    def CreateVehicle(token : str) :
        session_user = ValidationService.validate_session_token(token)
        pass

    @staticmethod
    def ActOnVehicle(token : str) :
        session_user = ValidationService.validate_session_token(token)
        pass

    #Put 
    @staticmethod
    def ChangeVehicle(token : str) :
        session_user = ValidationService.validate_session_token(token)
        pass

    #Delete
    @staticmethod
    def DeleteVehicle(token : str) :
        session_user = ValidationService.validate_session_token(token)
        pass

    #Get
    @staticmethod

    def get_all_vehicles_admin_user(token : str, user_name : str): 
        """Admin vehicle lookup for a user"""
        if ValidationService.check_valid_admin():
            vehicles = load_json("data/vehicles.json")
            user = user_name
            UserService.user_exists(user)
            return vehicles.get(user, {})
        return          
    
    @staticmethod
    def get_all_vehicles(token : str): 
        """Get all user vehicles """
        session_user = ValidationService.validate_session_token(token)
        vehicles = load_json("data/vehicles.json")
        user = session_user["username"]
        UserService.user_exists(user)
        return vehicles.get(user, {})

    @staticmethod
    def get_vehicle_reservations(token : str, vid : str): 
        """Get all vehicle reservations for a vehicle"""
        session_user = ValidationService.validate_session_token(token)

        VehicleService.checkForVehicle(session_user, vid)
        # TODO In the old code, it returned nothing. For the 'refactor' it was decided to mostly copy over the old code with the new methods applied. This should be changed later
        # self.send_response(200)
        # self.send_header("Content-type", "application/json")
        # self.end_headers()
        # self.wfile.write(json.dumps([]).encode("utf-8"))
        return
        

    @staticmethod
    def get_vehicle_history(token : str, vid : str): 
        """Get the vehicle history"""
        session_user = ValidationService.validate_session_token(token)

        VehicleService.checkForVehicle(session_user, vid)
        # TODO In the old code, it returned nothing. For the 'refactor' it was decided to mostly copy over the old code with the new methods applied. This should be changed later
        # self.send_response(200)
        # self.send_header("Content-type", "application/json")
        # self.end_headers()
        # self.wfile.write(json.dumps([]).encode("utf-8"))
        return
        
