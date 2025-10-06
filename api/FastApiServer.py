from fastapi import FastAPI, status, Header
from typing import Annotated, Optional
import uvicorn
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse
from models.parking_models import ParkingLotCreate, SessionStart, SessionStop, SessionResponse, ParkingLotResponse
from services.user_service import UserService
from services.parking_service import ParkingService

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

if __name__ == "__main__":
    uvicorn.run("FastApiServer:app", host="127.0.0.1", port=8000, reload=True)