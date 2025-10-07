from fastapi import FastAPI, status, Header, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Optional
import uvicorn
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse
from models.parking_models import ParkingLotCreate, SessionStart, SessionStop, SessionResponse, ParkingLotResponse
from services.user_service import UserService
from services.parking_service import ParkingService

app = FastAPI(title="MobyPark API", description="Parking management system API", version="1.0.0")
security = HTTPBearer(auto_error=False)  

def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract token from Authorization header"""
    if credentials:
        return credentials.credentials
    return None

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
    token: Optional[str] = Depends(get_token)
):
    """Start a parking session for a vehicle in the specified parking lot
    
    Requires Bearer token in Authorization header.
    """
    print(f"DEBUG: FastAPI received token: '{token}' (type: {type(token)})")  # Debug line
    return ParkingService.start_parking_session(lot_id, session_data, token)

@app.post("/parking-lots/{lot_id}/sessions/stop", response_model=SessionResponse)
async def stop_parking_session(
    lot_id: str,
    session_data: SessionStop,
    token: Optional[str] = Depends(get_token)
):
    """Stop a parking session for a vehicle in the specified parking lot
    
    Requires Bearer token in Authorization header.
    """
    return ParkingService.stop_parking_session(lot_id, session_data, token)

@app.post("/parking-lots", response_model=ParkingLotResponse, status_code=status.HTTP_201_CREATED)
async def create_parking_lot(
    parking_lot_data: ParkingLotCreate,
    token: Optional[str] = Depends(get_token)
):
    """Create a new parking lot (Admin only)
    
    Requires Bearer token in Authorization header with admin privileges.
    """
    return ParkingService.create_parking_lot(parking_lot_data, token)

if __name__ == "__main__":
    uvicorn.run("FastApiServer:app", host="127.0.0.1", port=8000, reload=True)