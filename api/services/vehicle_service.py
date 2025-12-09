from fastapi import HTTPException, status
from datetime import datetime
from models.vehicle_models import Vehicle
from models.user_models import User
from typing import Optional
from storage_utils import load_json
from services.validation_service import ValidationService
from storage_utils import load_vehicle_data, save_vehicle_data, load_parking_lot_data
from services.user_service import UserService
from loaddb import load_data
import storage_utils
class VehicleService:

    @staticmethod
    def getUserVehicleID(session_user : User ):
        """getUserVehicleIDs"""
        vehicles = load_vehicle_data()
        uvehicles = [v['id'] for v in vehicles if v['user_id'] == session_user['id']]
        return uvehicles
    
    @staticmethod
    def getUserVehicle(session_user : User, vid :str ):
        """getUserVehicle"""
        vehicles = load_vehicle_data()
        uvehicles = [v for v in vehicles if v["id"] == vid]
        return uvehicles
    @staticmethod 
    def liscensce_plate_for_id(vid: str):
        vehicles = load_vehicle_data()
        return [v['liscense_plate'] for v in vehicles if v["id"] == vid]
       
    @staticmethod
    def getUserVehicles(id : str):
        vehicles = load_vehicle_data()
        uvehicles = [v for v in vehicles if v["user_id"] == id]
        return uvehicles
        
    @staticmethod
    def checkForVehicle(session_user : User , Vid : str):
        """Check if the vehicle exists"""

        uvehicles = VehicleService.getUserVehicleID(session_user)
        if not Vid in uvehicles:
                            raise HTTPException(
                                status_code=status.HTTP_404_NOT_FOUND,
                                detail="Not Found"
                        )
    @staticmethod
    def check_for_parameters(data):
        for field in ["make", "license_plate"]:
            if not field in data:
                raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Require field missing", "field": field}
            )
        return
    
    @staticmethod
    def check_for_liscense_id(lid, session_user):
        vehicles = load_vehicle_data()
        # Extract ALL license plates from the system and normalize them (remove dashes)
        vehicle_lids = [v["license_plate"] for v in vehicles]
        
        if lid in vehicle_lids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"error": "Vehicle with this license plate already exists in the system", "license_plate": lid}
            )
        return
   

    #Post
    @staticmethod
    def create_vehicle(token: str, data: dict):
        session_user = ValidationService.validate_session_token(token)
        VehicleService.check_for_parameters(data)

        vehicles = load_json("data/vehicles.json")

        lid = data["license_plate"].replace("-", "")
        VehicleService.check_for_liscense_id(lid, session_user)

        new_vehicle = {
            "id": len(vehicles) + 1, 
            "user_id": session_user["id"],
            "license_plate": data["license_plate"],
            "make": data["make"],
            "model":data["model"],
            "color":data["color"],
            "year":data["year"],
            "created_at": datetime.now().isoformat()
        }

        vehicles.append(new_vehicle)

        save_vehicle_data(vehicles)
        return {"status": "Success", "vehicle": data}

    @staticmethod
    def ActOnVehicle(token : str, data : dict) :
        #Potentially arbirtary, the expected function of acting on a vehicle id might already be handled in parking_service
        # session_user = ValidationService.validate_session_token(token)
        # VehicleService.check_for_parameters(data)
        
        # lid = data["license_plate"].replace("-", "")
        # vehicles = load_vehicle_data()
        # if not "parkinglot" in data :
        #     raise HTTPException(
        #         status_code=status.HTTP_400_BAD_REQUEST,
        #         detail={"error": "Require field missing", "field": "parkinglot"}
        #     )
        # not VehicleService.check_for_liscense_id(lid, session_user)
        # return {"status": "Accepted", "vehicle": vehicles[session_user["username"]][lid]}
        pass
        
 

    #Put 
    @staticmethod
    def change_vehicle(token: str, vid: str, NewData: Vehicle):

        session_user = ValidationService.validate_session_token(token)
        VehicleService.checkForVehicle(session_user, vid)
        vehicles = load_vehicle_data()
        index = None
        for i, v in enumerate(vehicles):
            if v["id"] == vid and v["user_id"] == session_user["id"]:
                index = i
                break

        if index is None:
            raise ValueError(f"Vehicle with id {vid} not found for user {session_user['username']}")

    
        if not isinstance(NewData, dict):
            try:
                NewData = NewData.model_dump() 
            except AttributeError:
                try:
                    NewData = NewData.dict()     
                except AttributeError:
                    from dataclasses import asdict
                    NewData = asdict(NewData)    

        vehicles[index] = NewData
        save_vehicle_data(vehicles)
        return {"status": "Success", "vehicle": vehicles[index]}

       
    
    #Delete
    @staticmethod
    def delete_vehicle(token : str , vid : str) :
        vehicles = load_vehicle_data()
        session_user = ValidationService.validate_session_token(token)
        VehicleService.checkForVehicle(session_user, vid)
        cur_vehicle = [v for v in vehicles if v['id'] == vid][0]

        remaining = [v for v in vehicles if v.get("license_plate") != cur_vehicle['license_plate']]
        save_vehicle_data(remaining)

        updated_vehicles = load_vehicle_data()
        if all(v.get("license_plate") != cur_vehicle['license_plate'] for v in updated_vehicles) :
             return {"Status" : "Deleted"}
        return {"Status" : "Not Deleted"}
    
    # Method for retrieving vehicles, if the user_name parameter is not None the user needs to be an admin
    @staticmethod
    def get_all_vehicles(token: str, user_name: Optional[str] = None): 
        """Admin vehicle lookup for a user"""
        session_user = ValidationService.validate_session_token(token)
        target_user = None
        # find the target user by username
        if user_name : 
            target_user = UserService.user_exists(user_name)
            if not target_user:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

            # require admin privileges
        
            if not ValidationService.check_valid_admin(session_user):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin privileges required")
            # return vehicles for the target user's id
            return VehicleService.getUserVehicles(target_user["id"])
        # A search for the users own vehicles 
        else:
            return VehicleService.getUserVehicles(session_user["id"])

    @staticmethod
    def get_vehicle_reservations(token : str, vid : str): 
        """Get all vehicle reservations for a vehicle"""
        session_user = ValidationService.validate_session_token(token)
        
        VehicleService.checkForVehicle(session_user, vid)
        reservations = load_parking_lot_data()
        vehicle_reservations = [r for r in reservations if r['vehicle_id'] == vid]
        if not vehicle_reservations:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No reservations")
        return vehicle_reservations
        

    @staticmethod
    def get_vehicle_history(token : str, vid : str): 
        """Get the vehicle history"""
        session_user = ValidationService.validate_session_token(token)
        VehicleService.checkForVehicle(session_user, vid)
        lp = VehicleService.liscensce_plate_for_id(vid)
        ssn = load_data.load_parking_sessions()
        
        return [s for s in ssn if s["licenseplate"] == lp]