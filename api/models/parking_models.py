from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ParkingLotCreate(BaseModel):
    name: str
    location: str
    capacity: int
    hourly_rate: float

class SessionStart(BaseModel):
    licenseplate: str

class SessionStop(BaseModel):
    licenseplate: str

class SessionResponse(BaseModel):
    message: str
    licenseplate: str

class ParkingLotResponse(BaseModel):
    message: str
    parking_lot_id: str

class Session(BaseModel):
    licenseplate: str
    started: str
    stopped: Optional[str] = None
    user: str