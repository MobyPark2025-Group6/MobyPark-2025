from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ParkingLotBase(BaseModel):
    id: Optional[str] = None
    name: str
    location: str
    capacity: int
    adress: Optional[str] = None
    reserved: int = 0
    tariff: float = 0.0
    day_tariff: float = 0.0
    created_at: Optional[datetime] = None
    lat: Optional[float] = None
    lng: Optional[float] = None


class SessionStart(BaseModel):
    licenseplate: str

class SessionStop(BaseModel):
    licenseplate: str

class SessionResponse(BaseModel):
    message: str
    licenseplate: str
    started: Optional[str] = None
    stopped: Optional[str] = None
    cost: Optional[float] = None

class ParkingLotResponse(BaseModel):
    message: str
    parking_lot_id: str

class Session(BaseModel):
    licenseplate: str
    started: str
    stopped: Optional[str] = None
    user: str