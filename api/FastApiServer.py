from fastapi import FastAPI, status, Header
from typing import Annotated, Optional
import uvicorn
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse
from models.parking_models import ParkingLotCreate, SessionStart, SessionStop, SessionResponse, ParkingLotResponse
from services.user_service import UserService
from services.parking_service import ParkingService
from services.vehicle_service import VehicleService

app = FastAPI(title="MobyPark API", description="Parking management system API", version="1.0.0")

@app.get("/")
async def read_root():
    return {"message": "Welcome to MobyPark API!"}

@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """Register a new user account"""
    return UserService.create_user(user_data)

@app.post("/login", response_model=LoginResponse)
async def login_user(credentials: UserLogin):
    """Authenticate user and create session"""
    return UserService.authenticate_user(credentials)

@app.post("/parking-lots/{lot_id}/sessions/start", response_model=SessionResponse)
async def start_parking_session(
    lot_id: str,
    session_data: SessionStart,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Start a parking session for a vehicle in the specified parking lot
    
    Requires Authorization header with session token.
    """
    return ParkingService.start_parking_session(lot_id, session_data, authorization)

@app.post("/parking-lots/{lot_id}/sessions/stop", response_model=SessionResponse)
async def stop_parking_session(
    lot_id: str,
    session_data: SessionStop,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Stop a parking session for a vehicle in the specified parking lot
    
    Requires Authorization header with session token.
    """
    return ParkingService.stop_parking_session(lot_id, session_data, authorization)

@app.post("/parking-lots", response_model=ParkingLotResponse, status_code=status.HTTP_201_CREATED)
async def create_parking_lot(
    parking_lot_data: ParkingLotCreate,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Create a new parking lot (Admin only)
    
    Requires Authorization header with admin session token.
    """
    return ParkingService.create_parking_lot(parking_lot_data, authorization)

@app.get("/vehicles/{vehicle_id}/reservations", response_model=SessionResponse)
async def get_vehicle_id_reservations(
    vehicle_id : str,
    authorization: Annotated[Optional[str], Header()] = None
    
):
    """
    Acquire all reservations for a vehicle ID (currently none functional)
    """
    return VehicleService.get_vehicle_reservations(authorization, vehicle_id)

@app.get("/vehicles/{vehicle_id}/history", response_model=SessionResponse)
async def get_vehicle_id_history(
    vehicle_id : str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Acquire all history for a vehicle by ID (currently none functional)
    """
    return  VehicleService.get_vehicle_history(authorization, vehicle_id) 

@app.get("/vehicles/{user_name}", response_model=SessionResponse)
async def get_vehicles(
    user_name : str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Acquire all vehicles from a user as an admin
    """
    return VehicleService.get_all_vehicles_admin_user (authorization, user_name)

@app.get("/vehicles", response_model=SessionResponse)
async def get_vehicles(

    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Acquire all vehicles from the user
    """
    return VehicleService.get_all_vehicles(authorization)

@app.put("/vehicles/{vid}")
async def change_vehicle(
    vid: str,
    license_plate: str,
    name: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Change/update a vehicle's information
    
    Args:
        vid: Vehicle ID to update
        license_plate: Vehicle license plate
        name: Vehicle name/description
        authorization: Session token for authentication
    """
    return VehicleService.ChangeVehicle(authorization, vid, license_plate, name)

@app.post("/vehicles")
async def create_vehicle(
    vehicle_data: dict,
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Create a new vehicle
    
    Args:
        vehicle_data: Dictionary containing vehicle information (name, license_plate)
        authorization: Session token for authentication
    """
    return VehicleService.CreateVehicle(authorization, vehicle_data)

@app.post("/vehicles/{vid}/entry")
async def act_on_vehicle(
    vid: str,
    request: dict,
    authorization: str = Header(None, alias="Authorization")
):
    """Act on a vehicle (e.g., parking lot entry)"""
    return VehicleService.ActOnVehicle(authorization, vid, request)

@app.delete("/vehicles/{vid}")
async def delete_vehicle(
    vid: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Delete a vehicle
    
    Args:
        vid: Vehicle ID to delete
        authorization: Session token for authentication
    """
    return VehicleService.DeleteVehicle(authorization, vid)


if __name__ == "__main__":
    uvicorn.run("FastApiServer:app", host="127.0.0.1", port=8000, reload=True)