from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ParkingLotBase(BaseModel):
    id: int
    name: str
    location: str
    capacity: int
    adress : str 
    reserved : int
    tariff : float 
    day_tariff: float
    created_at : datetime
    lat : float
    lng : float


class SessionStart(BaseModel):
    licenseplate: str

class SessionStop(BaseModel):
    licenseplate: str

class SessionResponse(BaseModel):
    message: str
    licenseplate: str
    started: Optional[str] = None
    stopped: Optional[str] = None

class ParkingLotResponse(BaseModel):
    message: str
    parking_lot_id: str

class Session(BaseModel):
    licenseplate: str
    started: str
    stopped: Optional[str] = None
    user: str