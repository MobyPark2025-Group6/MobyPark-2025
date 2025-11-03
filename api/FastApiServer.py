from fastapi import FastAPI, status, Header, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Annotated, List, Optional
import uvicorn
from models.vehicle_models import *
from models.user_models import UserRegister, UserLogin, LoginResponse, MessageResponse, User
from models.parking_models import ParkingLotCreate, SessionStart, SessionStop, SessionResponse, ParkingLotResponse
from models.payment_models import PaymentCreate, PaymentRefund, PaymentUpdate, PaymentOut
from services.user_service import UserService
from services.parking_service import ParkingService
from services.vehicle_service import VehicleService
from services.payment_service import PaymentService

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

@app.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED, tags=["Authentication"])
async def register_user(user_data: UserRegister):
    """Register a new user account with optional extended information"""
    return UserService.create_user(user_data)

@app.post("/login", response_model=LoginResponse, tags=["Authentication"])
async def login_user(credentials: UserLogin):
    """Authenticate user credentials and create a session token"""
    return UserService.authenticate_user(credentials)

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

@app.delete("/users/{username}", response_model=MessageResponse, tags=["Users"])
async def delete_user_account(
    username: str,
    token: Optional[str] = Depends(get_token)
):
    """Delete a user account (Admin only)
    
    Requires Bearer token in Authorization header with admin privileges.
    Only users with ADMIN role can delete user accounts.
    """
    return UserService.delete_user(username, token)

@app.get("/users", response_model=List[User], tags=["Users"])
async def get_all_users(token: Optional[str] = Depends(get_token)):
    """Get a list of all users (Admin only)

    Requires Bearer token in Authorization header with admin privileges.
    Only users with ADMIN role can access this endpoint.
    """
    return UserService.get_all_users(token)

@app.get("/users/{username}/vehicles", response_model=List[Vehicle], tags=["Users"])
async def get_user_vehicles(
    username: str,
    token: Optional[str] = Depends(get_token)
):
    """Get a list of vehicles registered to the specified user
    
    Requires Bearer token in Authorization header.
    Users can only access their own vehicle list unless they have ADMIN role.
    """
    return UserService.get_user_vehicles(username, token)

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

from fastapi import Depends

@app.get("/payments", response_model=List[PaymentOut], tags=["Payments"])
async def get_payments(token: Optional[str] = Depends(get_token)):
    """Get all payments for the authenticated user"""
    session = PaymentService.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    return PaymentService.get_user_payments(session["username"])


@app.get("/payments/{username}", response_model=List[PaymentOut], tags=["Payments"])
async def get_user_payments(username: str, token: Optional[str] = Depends(get_token)):
    """Admin only: Get payments of a specific user"""
    session = PaymentService.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    try:
        return PaymentService.get_all_user_payments(session, username)
    except PermissionError:
        raise HTTPException(status_code=403, detail="Access denied")


@app.post("/payments", response_model=dict, status_code=201, tags=["Payments"])
async def create_payment(payment: PaymentCreate, token: Optional[str] = Depends(get_token)):
    """Create a new payment"""
    session = PaymentService.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    payment_obj = PaymentService.create_payment(payment, session)
    return {"status": "Success", "payment": payment_obj}


@app.post("/payments/refund", response_model=dict, status_code=201, tags=["Payments"])
async def refund_payment(payment: PaymentRefund, token: Optional[str] = Depends(get_token)):
    """Issue a refund (Admin only)"""
    session = PaymentService.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    if session["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Access denied")
    refund_obj = PaymentService.refund_payment(payment, session)
    return {"status": "Success", "payment": refund_obj}


@app.put("/payments/{transaction_id}", response_model=dict, tags=["Payments"])
async def update_payment(transaction_id: str, update: PaymentUpdate, token: Optional[str] = Depends(get_token)):
    """Complete or validate a payment transaction"""
    session = PaymentService.get_session(token)
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or missing token")
    try:
        updated_payment = PaymentService.update_payment(transaction_id, update)
        return {"status": "Success", "payment": updated_payment}
    except ValueError:
        raise HTTPException(status_code=404, detail="Payment not found")
    except PermissionError:
        raise HTTPException(status_code=401, detail="Validation failed")


# Placeholder endpoints for future implementation

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
    vehicle: Vehicle,
    authorization: Annotated[Optional[str], Header()] = None
):
    """
    Change/update a vehicle's information.
    
    Args:
        vid: Vehicle ID to update
        vehicle: Vehicle data to update (license_plate, name)
        authorization: Session token for authentication
    """
    return VehicleService.ChangeVehicle(
        authorization,
        vid,
        vehicle
    )

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

@app.post("/vehicles/{lid}/entry")
async def act_on_vehicle(
    lid: str,
    authorization: str = Header(None, alias="Authorization")
):
    """Act on a vehicle (e.g., parking lot entry)"""
    return VehicleService.ActOnVehicle(authorization, lid)

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