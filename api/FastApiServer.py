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

@app.get("/parking-lots", response_model=list[ParkingLotResponse])
async def list_parking_lots(
    authorization: Annotated[Optional[str], Header()] = None
):
    """List all parking lots.
    
    Requires Authorization header with valid session token.
    """
    return ParkingService.list_parking_lots(authorization)


@app.get("/parking-lots/{lot_id}", response_model=ParkingLotResponse)
async def get_parking_lot(
    lot_id: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Retrieve a specific parking lot by ID.
    
    Requires Authorization header with valid session token.
    """
    return ParkingService.get_parking_lot(lot_id, authorization)


@app.get("/parking-lots/{lot_id}/sessions", response_model=list[SessionResponse])
async def list_parking_sessions(
    lot_id: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """List all sessions in a parking lot.
    
    Requires Authorization header with session token.
    Admins see all sessions; users see only their own.
    """
    return ParkingService.list_parking_sessions(lot_id, authorization)


@app.get("/parking-lots/{lot_id}/sessions/{session_id}", response_model=SessionResponse)
async def get_parking_session(
    lot_id: str,
    session_id: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Get details of a specific parking session.
    
    Requires Authorization header with session token.
    Only Admins or the session owner can access.
    """
    return ParkingService.get_parking_session(lot_id, session_id, authorization)

@app.delete("/parking-lots/{lot_id}", status_code=status.HTTP_200_OK)
async def delete_parking_lot(
    lot_id: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Delete a parking lot (Admin only)."""
    return ParkingService.delete_parking_lot(lot_id, authorization)


@app.delete("/parking-lots/{lot_id}/sessions/{session_id}", status_code=status.HTTP_200_OK)
async def delete_parking_session(
    lot_id: str,
    session_id: str,
    authorization: Annotated[Optional[str], Header()] = None
):
    """Delete a specific parking session (Admin only)."""
    return ParkingService.delete_parking_session(lot_id, session_id, authorization)

# Placeholder endpoints for future implementation
@app.get("/payments", tags=["Payments"])
async def get_payments():
    """Get payment history (Coming Soon)"""
    return {"message": "Payments endpoint - Coming Soon"}

@app.post("/payments", tags=["Payments"])
async def create_payment():
    """Process a new payment (Coming Soon)"""
    return {"message": "Payment processing - Coming Soon"}

@app.get("/vehicles", tags=["Vehicles"])
async def get_vehicles():
    """Get user's registered vehicles (Coming Soon)"""
    return {"message": "Vehicles endpoint - Coming Soon"}

@app.post("/vehicles", tags=["Vehicles"])
async def register_vehicle():
    """Register a new vehicle (Coming Soon)"""
    return {"message": "Vehicle registration - Coming Soon"}

@app.get("/reservations", tags=["Reservations"])
async def get_reservations():
    """Get user's parking reservations (Coming Soon)"""
    return {"message": "Reservations endpoint - Coming Soon"}

@app.post("/reservations", tags=["Reservations"])
async def create_reservation():
    """Create a new parking reservation (Coming Soon)"""
    return {"message": "Reservation creation - Coming Soon"}

if __name__ == "__main__":
    uvicorn.run("FastApiServer:app", host="127.0.0.1", port=8000, reload=True)