from typing import Optional
from fastapi import HTTPException, status
import json
from datetime import datetime
from models.user_models import User
from storage_utils import load_json
from services.validation_service import ValidationService
from storage_utils import load_vehicle_data,save_data
from services.user_service import UserService
class VehicleService:
    @staticmethod
    def checkForVehicle(session_user : User , Vid : str):
        """Check if the vehicle exists"""
        vehicles = load_vehicle_data()
        uvehicles = [v["id"] for v in vehicles if v["user_id"] == session_user["id"]]
        if not Vid in uvehicles:
              raise HTTPException(
                status_code=status.HTTP_404_FORBIDDEN,
                detail="Not Found"
            )
        
    @staticmethod
    def check_for_parameters(data):
        for field in ["name", "license_plate"]:
            if not field in data:
                raise HTTPException(
                status_code=status.HTTP_401_FORBIDDEN,
                detail={"error": "Require field missing", "field": field}
            )
        return
    
    @staticmethod
    def check_for_liscense_id(lid, session_user):
        vehicles = load_json("data/vehicles.json")
        uvehicles = [v["license_plate"] for v in vehicles if v["user_id"] == session_user["id"]]

        if str(lid) in uvehicles:
                raise HTTPException(
                status_code=status.HTTP_401_FORBIDDEN,
                detail={"error": "Vehicle already exists", "data": uvehicles.get(lid)}
            )
        return
    @staticmethod
    def check_for_liscense_id_not_exists(lid,session_user ):
        vehicles = load_json("data/vehicles.json")
        uvehicles = vehicles.get(session_user["username"], {})
    
        if lid not in uvehicles:
                raise HTTPException(
                status_code=status.HTTP_401_FORBIDDEN,
                detail={"error": "Vehicle does not exist", "data": uvehicles.get(lid)}
            )
        return

    #Post
    @staticmethod
    def CreateVehicle(token: str, data: dict):
        session_user = ValidationService.validate_session_token(token)
        VehicleService.check_for_parameters(data)

        vehicles = load_json("data/vehicles.json")
        uvehicles = [v["id"] for v in vehicles if v["user_id"] == session_user["id"]]

        lid = data["license_plate"].replace("-", "")
        VehicleService.check_for_liscense_id(lid, session_user)

        new_vehicle = {
            "id": len(vehicles) + 1,  # of gebruik een uuid
            "user_id": session_user["id"],
            "licenseplate": data["license_plate"],
            "name": data["name"],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        vehicles.append(new_vehicle)

        save_data("data/vehicles.json", vehicles)
        return {"status": "Success", "vehicle": data}

    @staticmethod
    def ActOnVehicle(token : str, data : dict) :
        # session_user = ValidationService.validate_session_token(token)
        # ValidationService.check_for_parameters(data)
        
        # lid = data["license_plate"].replace("-", "")
        # vehicles = load_json("data/vehicles.json")
        # if not "parkinglot" in data :
        #     raise HTTPException(
        #         status_code=status.HTTP_401_FORBIDDEN,
        #         detail={"error": "Require field missing", "field": "parkinglot"}
        #     )
        # ValidationService.check_for_liscense_id_not_exists(lid, session_user)
        # return {"status": "Accepted", "vehicle": vehicles[session_user["username"]][lid]}
        return {"status" : "Not implemented"}
 

    #Put 
    @staticmethod
    def ChangeVehicle(token: str, vid: str, license_plate: Optional[str], name: Optional[str]):
        session_user = ValidationService.validate_session_token(token)
        username = session_user["username"]

        if not name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Required field missing: name"
            )

        vehicles = load_vehicle_data()
        user_vehicles = vehicles.get(username, {})

        # Ensure user key exists
        if username not in vehicles:
            vehicles[username] = {}

        # Create or update vehicle
        if vid not in user_vehicles:
            vehicles[username][vid] = {
                "license_plate": license_plate,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
            }
        else:
            vehicle = user_vehicles[vid]
            if license_plate:
                vehicle["license_plate"] = license_plate
            vehicle["name"] = name
            vehicle["updated_at"] = datetime.now().isoformat()

        save_data("data/vehicles.json", vehicles)

        return {
            "status": "Success",
            "vehicle": vehicles[username][vid]
        }
    
    #Delete
    @staticmethod
    def DeleteVehicle(token : str , vid : str) :
        session_user = ValidationService.validate_session_token(token)
        VehicleService.checkForVehicle(session_user, vid)
        vehicles = load_vehicle_data()
        del vehicles[session_user["username"]][vid]
        save_data("data/vehicles.json", vehicles)
        return {"status": "Deleted"}

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
        user_id = session_user["id"]
        UserService.user_exists(user)
        all_vehicles = [v for v in vehicles if v["user_id"] == user_id]
        return all_vehicles

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
        
