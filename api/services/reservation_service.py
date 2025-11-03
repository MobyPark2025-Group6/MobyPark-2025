from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from services.validation_service import ValidationService
from storage_utils import load_json, save_data, load_reservation_data, save_reservation_data
from models.reservation_models import ReservationRegister

class ReservationService:
    # post
    @staticmethod
    def create_reservation(reservation_data: ReservationRegister, token: str) -> Dict[str, Any]:
        """Create a new parking reservation"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)

        # Ensure the user is creating a reservation for themselves or is an admin
        if not ValidationService.check_valid_admin(session_user):
            if reservation_data.user_id != session_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            else:
                reservation_data.user_id = session_user["id"]

        # Load existing reservations
        reservations = load_reservation_data()

        # Create new reservation entry
        new_reservation = {
            "id": f"{len(reservations) + 1}",
            "user_id": reservation_data.user_id,
            "lot_id": reservation_data.lot_id,
            "vehicle_id": reservation_data.vehicle_id,
            "start_time": reservation_data.start_time,
            "end_time": reservation_data.end_time,
            "created_at": int(datetime.now().timestamp())
        }

        # Update parkinglots to show reservation

        # Save the new reservation
        reservations.append(new_reservation)
        save_reservation_data(reservations)

        return {"status": "Success" ,"reservation": new_reservation}

    # get
    @staticmethod
    def get_reservations_list(user_id: str, token: str) -> Dict[str, Any]:
        """Retrieve reservations for a specific user"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)
        if session_user["id"] != user_id and not ValidationService.check_valid_admin(session_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Cannot access other user's reservations"
            )
        
        # Ensure the user is getting their own reservations or is an admin
        if not ValidationService.check_valid_admin(session_user):
            if user_id != session_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

        reservations = load_reservation_data()

        user_reservations = [res for res in reservations if res["user_id"] == user_id]
        return {"reservations": user_reservations}
    
    @staticmethod
    def get_reservation(res_id: str, token: str) -> Dict[str, Any]:
        """Retrieve a specific reservation by its ID"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)

        reservations = load_reservation_data()
        reservation = next((res for res in reservations if res["id"] == res_id), None)

        if not reservation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )
        
        # Ensure the user is getting a reservation for themselves or is an admin
        if not ValidationService.check_valid_admin(session_user):
            if reservation.user_id != session_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

        return {"reservation": reservation}