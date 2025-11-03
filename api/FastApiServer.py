from fastapi import FastAPI, status, Header, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, Optional
import uvicorn
from models.reservation_models import ReservationRegister
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse, User
from models.parking_models import ParkingLotCreate, SessionStart, SessionStop, SessionResponse, ParkingLotResponse
from services.user_service import UserService
from services.parking_service import ParkingService
from services.reservation_service import ReservationService

# Define tags for API organization
tags_metadata = [
    {
        "name": "Authentication",
        "description": "User registration, login and authentication operations",
    },
    {
        "name": "Users",
        "description": "User management and profile operations",
    },
    {
        "name": "Parking Lots",
        "description": "Parking lot management and session operations",
    },
    {
        "name": "Payments",
        "description": "Payment processing and transaction operations",
    },
    {
        "name": "Vehicles",
        "description": "Vehicle registration and management operations",
    },
    {
        "name": "Reservations",
        "description": "Parking space reservation and booking operations",
    },
]

app = FastAPI(
    title="MobyPark API", 
    description="Comprehensive parking management system API with user authentication, parking lot management, payments, and reservations",
    version="1.0.0",
    openapi_tags=tags_metadata
)
security = HTTPBearer(auto_error=False)  

def get_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[str]:
    """Extract token from Authorization header"""
    if credentials:
        return credentials.credentials
    return None

@app.get("/", tags=["General"])
async def read_root():
    """Welcome endpoint with API information"""
    return {"message": "Welcome to MobyPark API!", "version": "1.0.0", "docs": "/docs"}

# Authentication Endpoints
@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserRegister):
    """Register a new user account with optional extended information"""
    return UserService.create_user(user_data)

@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login_user(credentials: UserLogin):
    """Authenticate user credentials and create a session token"""
    return UserService.authenticate_user(credentials)

# User Management Endpoints
@app.get("/users/{username}", response_model=User, tags=["Users"])
async def get_user_profile(username: str):
    """Get detailed user profile information by username"""
    user = UserService.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

# Parking Lot Management Endpoints
@app.post("/parking-lots", response_model=ParkingLotResponse, status_code=status.HTTP_201_CREATED, tags=["Parking Lots"])
async def create_parking_lot(
    parking_lot_data: ParkingLotCreate,
    token: Optional[str] = Depends(get_token)
):
    """Create a new parking lot (Admin only)
    
    Requires Bearer token in Authorization header with admin privileges.
    Only users with ADMIN role can create new parking lots.
    """
    return ParkingService.create_parking_lot(parking_lot_data, token)

@app.post("/parking-lots/{lot_id}/sessions/start", response_model=SessionResponse, tags=["Parking Lots"])
async def start_parking_session(
    lot_id: str,
    session_data: SessionStart,
    token: Optional[str] = Depends(get_token)
):
    """Start a parking session for a vehicle in the specified parking lot
    
    Requires Bearer token in Authorization header.
    Creates a new parking session with start time and links it to the authenticated user.
    """
    print(f"DEBUG: FastAPI received token: '{token}' (type: {type(token)})")  # Debug line
    return ParkingService.start_parking_session(lot_id, session_data, token)

@app.post("/parking-lots/{lot_id}/sessions/stop", response_model=SessionResponse, tags=["Parking Lots"])
async def stop_parking_session(
    lot_id: str,
    session_data: SessionStop,
    token: Optional[str] = Depends(get_token)
):
    """Stop a parking session for a vehicle in the specified parking lot
    
    Requires Bearer token in Authorization header.
    Ends an active parking session by setting the stop time.
    """
    return ParkingService.stop_parking_session(lot_id, session_data, token)

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

@app.get("/reservations/{res_id}", tags=["Reservations"])
async def get_reservations(
        res_id: str,
        token: Optional[str] = Depends(get_token)
    ):
    """Get reservation details by reservation ID

    Requires Bearer token in Authorization header.
    """
    return ReservationService.get_reservation(res_id, token)

@app.post("/reservations", tags=["Reservations"])
async def create_reservation(
        reservation_data: ReservationRegister,
        token: Optional[str] = Depends(get_token)
    ):
    """Create a new reservation
    
    Requires Bearer token in Authorization header.
    """
    return ReservationService.create_reservation(reservation_data, token)

if __name__ == "__main__":
    uvicorn.run("FastApiServer:app", host="127.0.0.1", port=8000, reload=True)