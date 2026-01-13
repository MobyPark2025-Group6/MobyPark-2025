from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from services.validation_service import ValidationService
from storage_utils import load_data_db_table, get_item_db, save_reservation
from storage_utils import create_data, delete_data, load_data_db_table, get_item_db, change_data
from storage_utils import create_data, delete_data, load_data_db_table, get_item_db
from models.reservation_models import ReservationRegister, ReservationResponse, ReservationOut

class ReservationService:
    # post
    @staticmethod
    def create_reservation(reservation_data: ReservationRegister, token: str) -> Dict[str, Any]:
        """Create a new parking reservation"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)

        # Ensure the user is creating a reservation for themselves or is an admin
        if not ValidationService.check_valid_admin(session_user) and not ValidationService.check_valid_admin(session_user) or ValidationService.check_valid_employee(session_user):
            if reservation_data.user_id != session_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            else:
                reservation_data.user_id = session_user["id"]

        parking_lots = load_data_db_table("parking_lots")

        # Check if parking lot has available spots
        lot = parking_lots.get(reservation_data.lot_id)
        if lot:
            if lot["reserved"] >= lot["capacity"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No available spots in the selected parking lot"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parking lot not found"
            )

        # Load existing reservations
        reservations = load_data_db_table("reservations")

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
        lot["reserved"] += 1
        parking_lots[reservation_data.lot_id] = lot
        change_data("parking_lots", parking_lots, )

        # Save the new reservation
        save_reservation.create_reservation(new_reservation)


        return {"status": "Success" ,"reservation": new_reservation}

    # get
    @staticmethod
    def get_reservations_list(user_id: str, token: str) -> Dict[str, Any]:
        """Retrieve reservations for a specific user"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)
        if session_user["id"] != user_id and not ValidationService.check_valid_admin(session_user) and not ValidationService.check_valid_employee(session_user):
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

        reservations = load_data_db_table("reservations")

        return [ReservationRegister(**reservation) for reservation in reservations if reservation["user_id"] == user_id]
    
    @staticmethod
    def get_reservation(res_id: str, token: str) -> Dict[str, Any]:
        """Retrieve a specific reservation by its ID"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)

        reservations = get_item_db("id", res_id, "reservations")

        if not reservations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )
        
        reservation = reservations[0]
        
        # Ensure the user is getting a reservation for themselves or is an admin
        if not ValidationService.check_valid_admin(session_user) and not ValidationService.check_valid_employee(session_user):
            if reservation["user_id"] != session_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )
            
        # Transform DB row to API schema (ReservationOut) with datetimes
        def to_dt(v):
            if isinstance(v, datetime):
                return v
            if isinstance(v, (int, float)):
                return datetime.fromtimestamp(int(v))
            if isinstance(v, str):
                for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"):
                    try:
                        return datetime.strptime(v.replace("Z", ""), fmt)
                    except ValueError:
                        continue
            raise HTTPException(status_code=500, detail="Invalid datetime value in reservation")

        out = {
            "id": str(reservation.get("id")) if reservation.get("id") is not None else None,
            "user_id": str(reservation.get("user_id")),
            "lot_id": str(reservation.get("parking_lot_id") or reservation.get("lot_id")),
            "vehicle_id": str(reservation.get("vehicle_id")),
            "start_time": to_dt(reservation.get("start_time")),
            "end_time": to_dt(reservation.get("end_time")),
            "created_at": to_dt(reservation.get("created_at")) if reservation.get("created_at") is not None else None,
            "cost": float(reservation.get("cost")) if reservation.get("cost") is not None else None,
            "status": reservation.get("status"),
        }
        # Validate and return as ReservationOut dict
        return ReservationOut(**out).model_dump()
    
    
    @staticmethod
    def delete_reservation(res_id: str, token: str) -> Dict[str, Any]:
        """Delete a specific reservation by its ID"""
        # Validate session token
        session_user = ValidationService.validate_session_token(token)

        reservations = load_data_db_table("reservations")
        reservation_index = next((i for i, res in enumerate(reservations) if res["id"] == res_id), None)

        if reservation_index is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reservation not found"
            )
        
        reservation = reservations[reservation_index]

        # Ensure the user is deleting a reservation for themselves or is an admin
        if not ValidationService.check_valid_admin(session_user):
            if reservation["user_id"] != session_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied"
                )

        # Update parking lot to free up the reserved spot
        parking_lots = load_data_db_table("parking_lots")
        lot = parking_lots.get(reservation["lot_id"])
        if lot and lot["reserved"] > 0:
            lot["reserved"] -= 1
            parking_lots[reservation["lot_id"]] = lot
            change_data("parking_lots", parking_lots, )

        # Remove the reservation
        reservations.pop(reservation_index)
        change_data("reservations", reservations, )
        delete_data(res_id, "reservation_id", "reservations")

        return {"status": "Success", "message": "Reservation deleted"}
