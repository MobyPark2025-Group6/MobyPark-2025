from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from storage_utils import  create_data, load_data_db_table, delete_data, get_item_db, create_data, change_data
from session_manager import get_session, add_session
from models.parking_models import (
    ParkingLotBase, SessionStart, SessionStop, 
    SessionResponse, ParkingLotResponse
)
import math 


# Setup system user voor automatische parkeerregistratie
system_user = {
    "id": "0",
    "username": "system",
    "role": "ADMIN",
    "hotel_guest": False,
    "active": True,
    "created_at": "2025-12-09"
}

system_token = "system-token"

# Voeg system user toe als hij nog niet bestaat
if not get_session(system_token):
    add_session(system_token, system_user)

def calculate_rate(minutes, start, pl_tariff,pl_dtariff):
    start = datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
    total_minutes = minutes
    total_days = ((total_minutes / 60) / 24) 

    m_r = (total_minutes/60) * pl_tariff

    # If the amount of days is less then one, return the tariff x minutes
    if total_days < 1:
        return m_r
    else:
        # Split of the days and the hours, for example math.modf(539.999) would return (0.999, 539.0)
        hours, days = math.modf(total_days)
        # The tariff on a day to day basis + the hours remaining x the hourly tariff 
        return (days * pl_dtariff) + ((hours * 24) * pl_tariff)
        
class ParkingService:
    @staticmethod
    def validate_session_token(token: Optional[str]) -> Dict[str, Any]:
        """Validate session token and return user data"""
        # print(f"DEBUG: Received token: '{token}' (type: {type(token)})")  # Debug line
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Missing session token"
            )
        
        session_user = get_session(token)
        # print(f"DEBUG: Session lookup result: {session_user}")  # Debug line
        if not session_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Invalid session token"
            )
        
        return session_user
    
    @staticmethod
    def validate_admin_access(user: Dict[str, Any]):
        """Check if user has admin access"""
        if user.get('role') != 'ADMIN':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Admin privileges required"
            )
    
    @staticmethod
    def start_parking_session(lot_id: str, session_data: SessionStart, token: Optional[str]) -> SessionResponse:
        """Start a parking session for a vehicle"""
        # Validate session token
        session_user = ParkingService.validate_session_token(token)
        
        # Load existing sessions for this parking lot
        # sessions = load_json(f'data/pdata/p{lot_id}-sessions.json')
        
        # Check if there's already an active session for this license plate
        filtered_sessions = [p for p in get_item_db('licenseplate', session_data.licenseplate, 'parking_sessions') if p['stopped'] == None]
   
        # filtered_sessions = {
        #     key: value for key, value in sessions.items() 
        #     if (value.get("licenseplate") == session_data.licenseplate and 
        #         not value.get('stopped'))
        # }
        
        if len(filtered_sessions) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot start a session when another session for this license plate is already active"
            )
        
        # Create new session
        new_session = {
            "parking_lot_id" : lot_id, 
            "licenseplate": session_data.licenseplate,
            "started": datetime.now().strftime("%y-%m-%d %H:%M:%S"),
            "stopped": None,
            "user": session_user["username"],
            "cost": 0 if session_user.get("hotel_guest") else None,
            "duration_minutes" : 0,

        }
        
        # Add session with new ID
        # session_id = str(len(sessions) + 1)
        # sessions[session_id] = new_session
        
        create_data("parking_sessions",new_session)
        # Save sessions
        # save_data(f'data/pdata/p{lot_id}-sessions.json', sessions)
        
        return SessionResponse(
            message="Session started successfully",
            licenseplate=session_data.licenseplate,
            started=new_session["started"]
        )
    
    @staticmethod
    def stop_parking_session(lot_id: str, session_data: SessionStop, token: Optional[str]) -> SessionResponse:
        """Stop a parking session for a vehicle"""
        # Validate session token
        session_user = ParkingService.validate_session_token(token)
        get_sessions_for_plate = get_item_db('licenseplate', session_data.licenseplate, 'parking_sessions')
        session = [s for s in get_sessions_for_plate if s['stopped'] == 'None' and s['user'] == session_user['username']]

        # Load existing sessions for this parking lot
        # sessions = load_json(f'data/pdata/p{lot_id}-sessions.json')
        
        # Find active session for this license plate
        # filtered_sessions = [p for p in get_item_db('licenseplate', session_data.licenseplate, 'parking_sessions') if p['stopped'] == None and p['']]
        pl = get_item_db('id',lot_id,'parking_lots')[0]
    
        
        if len(session) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cannot stop a session when there is no active session for this license plate"
            )
        
       
        # Get the first (and should be only) active session
        session = next(iter(session))

        # Update session with stop time

        session['stopped'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        session['payment_status'] = "pending"
        
        session['duration_minutes'] = ((datetime.strptime(session['stopped'], "%Y-%m-%d %H:%M:%S") -  datetime.strptime(session['started'] , "%Y-%m-%d %H:%M:%S") ).total_seconds() / 60.0)

        session['cost'] =  calculate_rate(session['duration_minutes'] , session['started'], float(pl['tariff']), float(pl['daytariff']))

  
        # Save sessions
        change_data('parking_sessions',session,'id')
        
        return SessionResponse(
            message="Session stopped successfully",
            licenseplate=session_data.licenseplate,
            stopped=session["stopped"]
        )

    # -------------------------
    # Auto system user parking
    # -------------------------

    @staticmethod
    def auto_start_parking(lot_id: str, license_plate: str) -> SessionResponse:
        """Start automatisch een parkeerregistratie voor system user"""
        return ParkingService.start_parking_session(
            lot_id,
            SessionStart(licenseplate=license_plate),
            system_token  # gebruikt de system user
        )

    @staticmethod
    def auto_stop_parking(lot_id: str, license_plate: str) -> SessionResponse:
        """Stop automatisch een parkeerregistratie voor system user"""
        return ParkingService.stop_parking_session(
            lot_id,
            SessionStop(licenseplate=license_plate),
            system_token
        )


    @staticmethod
    def create_parking_lot(parking_lot_data: ParkingLotBase, token: Optional[str]) -> ParkingLotResponse:
        """Create a new parking lot (Admin only)"""
        # Validate session token
        session_user = ParkingService.validate_session_token(token)        
        # Validate admin access
        ParkingService.validate_admin_access(session_user)        

        new_lot = {
            "name": parking_lot_data.name,
            "location": parking_lot_data.location,
            "capacity": parking_lot_data.capacity,
            "adress": parking_lot_data.adress,
            "reserved":parking_lot_data.reserved,
            "tariff":parking_lot_data.tariff,
            "day_tariff":parking_lot_data.day_tariff,
            "created_at":parking_lot_data.created_at,
            "lat":parking_lot_data.lat,
            "lng":parking_lot_data.lng


        }
        # Save parking lots
        create_data('parking_lots',new_lot)
        return ParkingLotResponse(
            message="Parking lot created successfully",
            parking_lot_name=new_lot["name"]
        )
    
    @staticmethod
    def list_parking_lots(token: Optional[str]):
        # Load and optionally filter data
        parking_lots = load_data_db_table("parking_lots")
        return parking_lots

    @staticmethod
    def get_parking_lot(lot_id: str, token: Optional[str]):
        parking_lot = get_item_db('id',lot_id,'parking_lots')
        if not parking_lot:
            raise HTTPException(status_code=404, detail="Parking lot not found")
        return parking_lot

    @staticmethod
    def list_parking_sessions(lot_id: str, token: Optional[str]):
        session_user = get_session(token)
        if not session_user:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session token")

        sessions = get_item_db('id',lot_id,'parking_lots')
        if session_user["role"] == "ADMIN":
            return sessions

        return [s for s in sessions if s["user"] == session_user["username"]]

    @staticmethod
    def get_parking_session(lot_id: str, session_id: str, token: Optional[str]):
        session_user = get_session(token)
        if not session_user:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session token")

        sessions = get_item_db('id',lot_id,'parking_lots')

        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="Session not found")

        session = [s for s in sessions if s['id'] == session_id]

        if session_user["role"] != "ADMIN" and session["user"] != session_user["username"]:
            raise HTTPException(status_code=403, detail="Access denied")

        return session
    
    @staticmethod
    def update_parking_lot(lot_id: str, updates: dict, token: Optional[str]):
        """Update a parking lot (Admin only)"""
        session_user = ParkingService.validate_session_token(token)
        ParkingService.validate_admin_access(session_user)

        parking_lots = get_item_db('id',lot_id,'parking_lots')
        if parking_lots:
            raise HTTPException(status_code=404, detail="Parking lot not found")
        change_data('parking_lots',updates,'id')
        # allowed_fields = ["name", "location", "capacity", "hourly_rate"]
        # for key in allowed_fields:
        #     if key in updates:
        #         parking_lots[lot_id][key] = updates[key]

        create_data(parking_lots)
        return {"message": "Parking lot updated successfully", "parking_lot_id": lot_id}


    @staticmethod
    def update_parking_session(lot_id: str, session_id: str, updates: dict, token: Optional[str]):
        """Update a parking session (Admin only)"""
        # Valideer token en admin access
        session_user = ParkingService.validate_session_token(token)
        ParkingService.validate_admin_access(session_user)

        # Laad bestaande sessies
        
        session = get_item_db('id',session_id,'parking_sessions')
        if session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Alleen toegestane velden updaten
        change_data('parking_sessions',session[0],'id')

        return session

    @staticmethod
    def delete_parking_lot(lot_id: str, token: Optional[str]):
        session_user = get_session(token)
        if not session_user:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session token")
        if session_user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Access denied")
        # TODO Removable?
        # parking_lots = load_data_db_table("parking_lots")
        # if lot_id not in parking_lots:
        #     raise HTTPException(status_code=404, detail="Parking lot not found")
        delete_data(lot_id,'id',"parking_lots")
  
        return {"detail": "Parking lot deleted"}

    @staticmethod
    def delete_parking_session(lot_id: str, session_id: str, token: Optional[str]):
        session_user = get_session(token)
        if not session_user:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid or missing session token")
        if session_user.get("role") != "ADMIN":
            raise HTTPException(status_code=403, detail="Access denied")

        delete_data(session_id,'id',"parking_sessions")
        return {"detail": "Session deleted"}