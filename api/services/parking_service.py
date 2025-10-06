from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException, status
from storage_utils import load_json, save_data, load_parking_lot_data, save_parking_lot_data
from session_manager import get_session
from models.parking_models import (
    ParkingLotCreate, SessionStart, SessionStop, 
    SessionResponse, ParkingLotResponse
)

class ParkingService:
    @staticmethod
    def validate_session_token(token: str) -> Dict[str, Any]:
        """Validate session token and return user data"""
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unauthorized: Missing session token"
            )
        
        session_user = get_session(token)
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
    def start_parking_session(lot_id: str, session_data: SessionStart, token: str) -> SessionResponse:
        """Start a parking session for a vehicle"""
        # Validate session token
        session_user = ParkingService.validate_session_token(token)
        
        # Load existing sessions for this parking lot
        sessions = load_json(f'data/pdata/p{lot_id}-sessions.json')
        
        # Check if there's already an active session for this license plate
        filtered_sessions = {
            key: value for key, value in sessions.items() 
            if (value.get("licenseplate") == session_data.licenseplate and 
                not value.get('stopped'))
        }
        
        if len(filtered_sessions) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot start a session when another session for this license plate is already active"
            )
        
        # Create new session
        new_session = {
            "licenseplate": session_data.licenseplate,
            "started": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
            "stopped": None,
            "user": session_user["username"]
        }
        
        # Add session with new ID
        session_id = str(len(sessions) + 1)
        sessions[session_id] = new_session
        
        # Save sessions
        save_data(f'data/pdata/p{lot_id}-sessions.json', sessions)
        
        return SessionResponse(
            message="Session started successfully",
            licenseplate=session_data.licenseplate
        )
    
    @staticmethod
    def stop_parking_session(lot_id: str, session_data: SessionStop, token: str) -> SessionResponse:
        """Stop a parking session for a vehicle"""
        # Validate session token
        session_user = ParkingService.validate_session_token(token)
        
        # Load existing sessions for this parking lot
        sessions = load_json(f'data/pdata/p{lot_id}-sessions.json')
        
        # Find active session for this license plate
        filtered_sessions = {
            key: value for key, value in sessions.items() 
            if (value.get("licenseplate") == session_data.licenseplate and 
                not value.get('stopped'))
        }
        
        if len(filtered_sessions) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cannot stop a session when there is no active session for this license plate"
            )
        
        # Get the first (and should be only) active session
        session_id = next(iter(filtered_sessions))
        
        # Update session with stop time
        sessions[session_id]["stopped"] = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        
        # Save sessions
        save_data(f'data/pdata/p{lot_id}-sessions.json', sessions)
        
        return SessionResponse(
            message="Session stopped successfully",
            licenseplate=session_data.licenseplate
        )
    
    @staticmethod
    def create_parking_lot(parking_lot_data: ParkingLotCreate, token: str) -> ParkingLotResponse:
        """Create a new parking lot (Admin only)"""
        # Validate session token
        session_user = ParkingService.validate_session_token(token)
        
        # Validate admin access
        ParkingService.validate_admin_access(session_user)
        
        # Load existing parking lots
        parking_lots = load_parking_lot_data()
        
        # Create new parking lot ID
        new_lot_id = str(len(parking_lots) + 1)
        
        # Add new parking lot
        parking_lots[new_lot_id] = {
            "name": parking_lot_data.name,
            "location": parking_lot_data.location,
            "capacity": parking_lot_data.capacity,
            "hourly_rate": parking_lot_data.hourly_rate
        }
        
        # Save parking lots
        save_parking_lot_data(parking_lots)
        
        return ParkingLotResponse(
            message="Parking lot created successfully",
            parking_lot_id=new_lot_id
        )